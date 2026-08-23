#!/usr/bin/env python3
"""Propagate the "auto-cancel superseded pipelines" CI change to the projects that
really saturate the runners, ranked by how many pipelines they created.

Background: vauxoo/project-template!152 (commit a5872891) added to the generated
".gitlab-ci.yml"

    workflow:
      auto_cancel:
        on_new_commit: interruptible

    default:
      interruptible: true

The instance-wide "Auto-cancel redundant pipelines" setting only cancels *pending*
jobs; a job already running on a runner is cancelled only when it is marked
"interruptible". That MR fixes new/regenerated projects only, so the existing ones
need this one-time mass update.

Pipelines are created mostly in the "*-dev" forks, but the file to patch lives in the
origin project (without "-dev"): a dev branch is created from the origin base branch
and inherits its ".gitlab-ci.yml". So counts of "<ns>-dev/<project>" are added to
"<ns>/<project>", and dev refs ("19.0-something-moy") are normalized to their base
branch ("19.0").

Ranking uses "push" + "merge_request_event" pipelines only: a "schedule" pipeline is
never superseded by a new commit, so "interruptible" does not help there.

A MR is opened for:

  1. the "--top" busiest (project, branch) of the measurement
  2. every stable branch of the projects maintained in several of them at once: the ones
     that showed more than one active branch in the measurement, from
     "--multibranch-from" (15.0) on, plus the MULTIBRANCH ones with their own floor
  3. every default branch of the "--group" client groups, no matter their pipeline count

Each MR CCs whoever merges there, taken from the last "--mergers-sample" merged MRs of
the project, or the fixed reviewers of GROUP_CC. The commit carries "[ci skip]": nothing
to test, and running a pipeline would defeat the purpose.

Usage:

    # dry run, just print the ranking and the selection (default)
    ./ci_pipelines_interruptible.py

    # open the MRs
    ./ci_pipelines_interruptible.py --apply

    # open the MR of a couple of known projects, without measuring anything again
    ./ci_pipelines_interruptible.py --apply --tag-mergers 0 \\
        --only nhomar/www.nhomar.com@19.0 --only luisg123v/skills@main
"""

# pylint: disable=print-used
import argparse
import collections
import functools
import re
import threading
from concurrent.futures import ThreadPoolExecutor

import gitlab

from gitlab_api import GitlabAPI

BRANCH_DEV_NAME = "ci-interruptible-moy"
DOCKERV_IMAGE = "image: quay.io/vauxoo/dockerv"
CI_FNAME = ".gitlab-ci.yml"
# The "timeout = 5" of ~/.python-gitlab.cfg is not enough for the big listings
TIMEOUT = 120
BASE_REF = re.compile(r"^(\d{1,2}\.\d)(?=$|[-_/.])")
STABLE_BRANCH = re.compile(r"^(\d{1,2}\.0)$")
# Pipeline sources cancelled by "workflow:auto_cancel:on_new_commit: interruptible"
SUPERSEDABLE_SOURCES = ("push", "merge_request_event")

COMMIT_MSG = """[IMP] .gitlab-ci.yml: auto-cancel superseded pipelines

Pushing a new commit to a branch currently leaves the previous pipeline
running to completion: the "Auto-cancel redundant pipelines" project
setting (already enabled instance-wide) only cancels jobs that are still
pending, never jobs already running on a runner, and Odoo test jobs run
for a long time. With frequent commits the pipelines pile up in the
queue, wasting runners and hitting external rate limits such as the
GitHub one for the entrypoint install.

Mark every generated job as interruptible and declare the auto-cancel
workflow explicitly, so a new commit on the same branch cancels the
superseded pipeline even when its jobs are already running.

Propagates vauxoo/project-template!152 to this project.

Only the CI declaration changes, there is nothing to test here and the whole
point is to stop wasting runners, so do not run a pipeline for this commit.

[ci skip]
"""

# Projects whose reviewers are fixed instead of taken from who merged the last MRs
GROUP_CC = {"jarsa": ["alan196", "HectorMerazChavez"]}
# Projects maintained in several stable branches at once, and the oldest one to fix.
# The measurement adds any other project that showed more than one active branch.
MULTIBRANCH = {
    "mexico/l10n-mx-edi-hr-expense": 14.0,
    "mexico/mexico": 14.0,
    "vauxoo/costarica": 14.0,
    "vauxoo/l10n-edi-hr-expense": 14.0,
    "vauxoo/l10n-mx-payroll": 14.0,
    "vauxoo/mexico-document": 14.0,
    "vauxoo/opencfdi-server": 14.0,
}
# Client projects just migrated: the older branches show up in the measurement but are
# not used anymore, only their default branch is
DEFAULT_BRANCH_ONLY = ("vauxoo/tanner", "vauxoo/tanner-common")

# ".gitlab-ci.yml" classification of a given (origin project, base branch)
STATE_DONE = "YA"  # already declares "interruptible", nothing to do
STATE_APPLY = "APLICA"  # project-template CI without "interruptible"
STATE_OTHER = "otro-CI"  # a CI that is not the project-template one
STATE_MISSING = "n/a"  # the branch or the CI file does not exist anymore
STATE_OPENED = "MR-abierto"  # a previous run already opened its MR, do not touch it

# Why a (project, branch) made it into the selection
WHY_MEASURED = "medido"
WHY_ONLY = "solicitado"
WHY_MULTIBRANCH = "multi-branch"
WHY_GROUP = "grupo %s"
WHY_DEFAULT = "default branch"

_LOCAL = threading.local()


def api():
    """One gitlab connection per thread, they are not thread safe"""
    if not hasattr(_LOCAL, "gitlab_api"):
        _LOCAL.gitlab_api = gitlab.Gitlab.from_config("default")
        _LOCAL.gitlab_api.timeout = TIMEOUT
    return _LOCAL.gitlab_api


def origin_path(path_with_namespace):
    """vauxoo-dev/mexico -> vauxoo/mexico"""
    namespace, _sep, name = path_with_namespace.partition("/")
    if namespace.endswith("-dev"):
        return "%s/%s" % (namespace[: -len("-dev")], name)
    return path_with_namespace


def base_ref(ref):
    """19.0-my-feature-moy -> 19.0 (master and main are kept as they are)"""
    match = BASE_REF.match(ref)
    if match:
        return match.group(1)
    if ref.startswith("refs/merge-requests"):
        return "(mr-ref)"
    return ref


def count_pipelines(project, created_after):
    """Cheap pipeline count: the X-Total header of a 1-item page"""
    try:
        response = api().http_request(
            "get",
            "/projects/%s/pipelines" % project["id"],
            query_data={"per_page": 1, "created_after": created_after},
        )
        return int(response.headers.get("X-Total") or 0)
    except (gitlab.exceptions.GitlabError, ValueError) as err:
        print("Couldn't count pipelines of %s: %s" % (project["path"], err))
        return 0


def refs_of_project(project, created_after, max_pages=80):
    """Full pagination of a project pipelines grouped by (base branch, source)"""
    counter = collections.Counter()
    page = 1
    while page <= max_pages:
        response = api().http_request(
            "get",
            "/projects/%s/pipelines" % project["id"],
            query_data={"per_page": 100, "page": page, "created_after": created_after},
        )
        pipelines = response.json()
        if not pipelines:
            break
        for pipeline in pipelines:
            counter[(base_ref(pipeline["ref"]), pipeline.get("source"))] += 1
        if len(pipelines) < 100:
            break
        page += 1
    return counter


@functools.lru_cache(maxsize=None)
def ci_state(origin, ref):
    """Classify the .gitlab-ci.yml of a branch of the origin project"""
    try:
        content = api().projects.get(origin).files.get(CI_FNAME, ref).decode().decode("utf-8", "replace")
    except (gitlab.exceptions.GitlabError, UnicodeDecodeError):
        return STATE_MISSING
    if "interruptible" in content:
        return STATE_DONE
    if content.lstrip().startswith(DOCKERV_IMAGE):
        return STATE_APPLY
    return STATE_OTHER


@functools.lru_cache(maxsize=None)
def has_open_mr(origin, ref):
    """True when this (project, branch) already got its MR from a previous run

    make_mr deletes and recreates its dev branch, which closes the MR opened before,
    losing its reviews. Skipping is also what makes a partial run resumable.
    """
    try:
        project = api().projects.get(origin)
    except gitlab.exceptions.GitlabError:
        return False
    source_branch = "%s-%s" % (ref, BRANCH_DEV_NAME)
    return bool(
        project.mergerequests.list(state="opened", source_branch=source_branch, target_branch=ref, get_all=False)
    )


def rank(year, probe_top, workers):
    """[(origin, base branch, superseded-able pipelines, scheduled ones, ci state)] desc"""
    created_after = "%d-01-01T00:00:00Z" % year
    gitlab_api = api()
    print("Listing projects...")
    projects = [
        {"id": project.id, "path": project.path_with_namespace}
        for project in gitlab_api.projects.list(iterator=True, archived=False, per_page=100)
    ]
    print("Counting %s pipelines of %d projects..." % (year, len(projects)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        counts = list(executor.map(lambda project: count_pipelines(project, created_after), projects))

    by_origin = collections.Counter()
    members = collections.defaultdict(list)
    for project, count in zip(projects, counts):
        origin = origin_path(project["path"])
        by_origin[origin] += count
        if count:
            members[origin].append(project)
    print("Total pipelines created since %s: %d" % (created_after, sum(counts)))

    top_origins = [origin for origin, _count in by_origin.most_common(probe_top) if by_origin[origin]]
    print("Getting the branches of the %d busiest projects..." % len(top_origins))

    def scan(origin):
        counter = collections.Counter()
        for project in members[origin]:
            counter.update(refs_of_project(project, created_after))
        return origin, counter

    rows = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for origin, counter in executor.map(scan, top_origins):
            by_ref = collections.defaultdict(collections.Counter)
            for (ref, source), count in counter.items():
                by_ref[ref][source] += count
            for ref, sources in by_ref.items():
                rows.append(
                    [
                        origin,
                        ref,
                        sum(sources[source] for source in SUPERSEDABLE_SOURCES),
                        sources["schedule"],
                        None,
                    ]
                )
    rows.sort(key=lambda row: -row[2])
    return rows


def stable_branches(origin, min_version):
    """Stable branches of a project, newest first, from min_version on"""
    branches = []
    try:
        project = api().projects.get(origin)
    except gitlab.exceptions.GitlabError:
        return branches
    for branch in project.branches.list(iterator=True, per_page=100):
        match = STABLE_BRANCH.match(branch.name)
        if match and float(match.group(1)) >= min_version:
            branches.append(branch.name)
    return sorted(branches, key=float, reverse=True)


def group_default_branches(group_path):
    """(project, default branch) of every project owned by a group, forks excluded

    A client group is expected to consume way less CI than a Vauxoo base project, so
    every one of its projects is worth fixing no matter its pipeline count.
    """
    gitlab_api = api()
    for group_project in gitlab_api.groups.get(group_path).projects.list(
        get_all=True, archived=False, include_subgroups=True
    ):
        if not group_project.path_with_namespace.startswith("%s/" % group_path):
            # Shared into the group, owned by somebody else
            continue
        project = gitlab_api.projects.get(group_project.id)
        if getattr(project, "forked_from_project", None):
            continue
        if project.default_branch:
            yield project.path_with_namespace, project.default_branch


def select(rows, args):
    """[(project, branch, push+MR, schedule, why)] to open a MR for

    3 sources, in this order, without duplicates:
      1. the "--top" busiest (project, branch) of the measurement
      2. every "--multibranch-from" branch of the projects that showed more than one
         active branch there, they are actively maintained in parallel
      3. every default branch of "--group", the client groups to fix as a whole
    """
    selected = []
    seen = set()
    measured = {}

    def add(origin, ref, why):
        if (origin, ref) in seen:
            return False
        seen.add((origin, ref))
        if ci_state(origin, ref) != STATE_APPLY or has_open_mr(origin, ref):
            return False
        superseded, scheduled = measured.get((origin, ref), (0, 0))
        selected.append([origin, ref, superseded, scheduled, why])
        return True

    print("\n%-45s %-9s %8s %8s  %s" % ("project", "branch", "push+MR", "schedule", "%s state" % CI_FNAME))
    for origin, ref, superseded, scheduled, _state in rows:
        measured[(origin, ref)] = (superseded, scheduled)
        if superseded < args.min_pipelines:
            break
        state = ci_state(origin, ref)
        mark = ""
        if state == STATE_APPLY and has_open_mr(origin, ref):
            state = STATE_OPENED
        elif state == STATE_APPLY and len(selected) < args.top:
            # Only the picked ones are "seen": a row left out by --top is still a valid
            # candidate for the multi-branch expansion below
            seen.add((origin, ref))
            selected.append([origin, ref, superseded, scheduled, WHY_MEASURED])
            mark = " <-- #%d" % len(selected)
        print("%-45s %-9s %8d %8d  %-8s%s" % (origin, ref, superseded, scheduled, state, mark))

    counter = collections.Counter(row[0] for row in selected)
    multibranch = {origin: args.multibranch_from for origin, count in counter.items() if count > 1}
    multibranch.update(MULTIBRANCH)
    for origin in DEFAULT_BRANCH_ONLY:
        multibranch.pop(origin, None)
        selected[:] = [row for row in selected if row[0] != origin]
        seen -= {(project, ref) for project, ref in seen if project == origin}
    for origin in sorted(multibranch):
        for ref in stable_branches(origin, multibranch[origin]):
            add(origin, ref, WHY_MULTIBRANCH)

    for origin in DEFAULT_BRANCH_ONLY:
        try:
            add(origin, api().projects.get(origin).default_branch, WHY_DEFAULT)
        except gitlab.exceptions.GitlabError as err:
            print("Couldn't get the default branch of %s: %s" % (origin, err))

    for group_path in args.group:
        for origin, ref in group_default_branches(group_path):
            add(origin, ref, WHY_GROUP % group_path)

    selected.sort(key=lambda row: (-row[2], row[0], row[1]))
    return selected


def group_targets(group_paths):
    """["ai"] -> ["ai/project@default-branch", ...], the whole group without measuring it"""
    targets = []
    for group_path in group_paths:
        for origin, ref in group_default_branches(group_path):
            targets.append("%s@%s" % (origin, ref))
    return targets


def only(projects_branches):
    """Same selection as select(), for an explicit ["project@branch"] list

    Nothing is measured here: the (project, branch) are already known, so the only
    request per row is reading its ".gitlab-ci.yml" to skip the ones that do not carry
    the project-template CI or already declare "interruptible".
    """
    selected = []
    seen = set()
    for project_branch in projects_branches:
        origin, _sep, ref = project_branch.partition("@")
        origin, ref = origin.strip(), ref.strip()
        if not origin or not ref:
            raise UserWarning('--only needs the format "OWNER/PROJECT@BRANCH", got "%s"' % project_branch)
        if (origin, ref) in seen:
            continue
        seen.add((origin, ref))
        state = ci_state(origin, ref)
        if state != STATE_APPLY:
            print("Skipping %s@%s, its %s is %s" % (origin, ref, CI_FNAME, state))
            continue
        selected.append([origin, ref, 0, 0, WHY_ONLY])
    return selected


def top_mergers(project, sample, count):
    """Usernames that merged the most of the last <sample> merged MRs of a project

    Whoever merges is in practice the project leader, the one to ask for the review.
    """
    counter = collections.Counter()
    for merged in project.mergerequests.list(
        state="merged", order_by="updated_at", sort="desc", get_all=False, per_page=sample
    ):
        full = project.mergerequests.get(merged.iid)
        user = (full.merge_user or getattr(full, "merged_by", None) or {}).get("username")
        if user:
            counter[user] += 1
    return [user for user, _count in counter.most_common(count)]


def tag_mergers(mrs, sample, count):
    """CC the usual mergers of each project in the MR description, not in the commit"""
    gitlab_api = api()
    cache = {}
    for mr in mrs:
        # make_mr returns the MR bound to the source project, but the iid and the merged
        # history both belong to the target one
        project = gitlab_api.projects.get(mr.target_project_id)
        if project.id not in cache:
            group = project.path_with_namespace.split("/")[0]
            cache[project.id] = GROUP_CC.get(group) or top_mergers(project, sample, count)
        if not cache[project.id]:
            print("No merger found to CC in %s" % mr.web_url)
            continue
        cc = "CC %s" % " ".join("@%s" % user for user in cache[project.id])
        target_mr = project.mergerequests.get(mr.iid)
        if cc in (target_mr.description or ""):
            continue
        target_mr.description = "%s\n\n%s\n" % ((target_mr.description or "").rstrip(), cc)
        target_mr.save()
        print("%s %s" % (target_mr.web_url, cc))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--year", type=int, default=2026, help="Count pipelines created since january 1st of it")
    parser.add_argument("--top", type=int, default=40, help="How many actionable (project, branch) to work on")
    parser.add_argument("--probe-top", type=int, default=120, help="How many busiest projects to break down by branch")
    parser.add_argument("--min-pipelines", type=int, default=25, help="Ignore branches below this many pipelines")
    parser.add_argument("--workers", type=int, default=12, help="Parallel API calls")
    parser.add_argument(
        "--multibranch-from",
        type=float,
        default=15.0,
        help="Oldest odoo version to fix in the projects maintained in several branches at once",
    )
    parser.add_argument(
        "--group",
        action="append",
        default=["jarsa"],
        help="Group whose projects are all fixed in their default branch, no matter their pipeline count",
    )
    parser.add_argument(
        "--tag-mergers",
        type=int,
        default=2,
        help="CC that many of the usual mergers of each project in the MR description, 0 to skip",
    )
    parser.add_argument("--mergers-sample", type=int, default=10, help="Last merged MRs to look at per project")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="PROJECT@BRANCH",
        help='Open the MR just for these "project@branch", repeatable. Skips the whole '
        "measurement and the merger lookup: no pipeline, MR or issue listing is done, "
        "only the .gitlab-ci.yml of each branch is read",
    )
    parser.add_argument(
        "--only-group",
        action="append",
        default=[],
        metavar="GROUP",
        help="Like --only, expanded to the default branch of every project owned by this "
        "group. Unlike --group it does not measure anything either",
    )
    parser.add_argument("--task-id", default=None, help="Odoo task ID to add to the MR titles")
    parser.add_argument("--apply", action="store_true", help="Create the MRs (dry run by default)")
    args = parser.parse_args()

    targets = list(args.only) + group_targets(args.only_group)
    selected = only(targets) if targets else select(rank(args.year, args.probe_top, args.workers), args)
    print("\n%-45s %-9s %8s %8s  %s" % ("project", "branch", "push+MR", "schedule", "why"))
    for origin, ref, superseded, scheduled, why in selected:
        print("%-45s %-9s %8d %8d  %s" % (origin, ref, superseded, scheduled, why))
    print(
        "\n%d MR to open on %d projects, covering %d push+MR pipelines of %s"
        % (
            len(selected),
            len({row[0] for row in selected}),
            sum(row[2] for row in selected),
            args.year,
        )
    )
    projects_branches = ["%s@%s" % (row[0], row[1]) for row in selected]
    if not args.apply:
        print("Dry run, nothing was created. Re-run with --apply to open the MRs.")
        return
    mrs = GitlabAPI().make_mr(
        projects_branches,
        COMMIT_MSG,
        BRANCH_DEV_NAME,
        task_id=args.task_id,
        prefix_version=True,
        run_pre_commit_vauxoo=False,
        require_modules=False,
    )
    if args.tag_mergers:
        tag_mergers(mrs, args.mergers_sample, args.tag_mergers)


if __name__ == "__main__":
    main()
