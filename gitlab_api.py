#!/usr/local/bin/python3

# pylint: disable=print-used,useless-object-inheritance
# TODO: Use logging
import csv
import os
import re
import shutil
import subprocess
import tempfile
import urllib.parse
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime

import jinja2
from click.testing import CliRunner

try:
    import gitlab
    from gitlab.exceptions import GitlabGetError
except ImportError:
    print("Please, install pip install python-gitlab==3.9.0")
    raise

try:
    from pre_commit_vauxoo import cli as pcv_cli
except ImportError:
    pcv_cli = None

CFG = os.path.expanduser("~/.python-gitlab.cfg")


@contextmanager
def chdir(directory):
    original_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(original_dir)


class GitlabAPI:
    """Custom functions using python-gitlab API

        In order to use the API you need to have a config file in your $HOME, you can find an example here:
        https://python-gitlab.readthedocs.io/
        Make sure to have a [default] section as that is the one used in this script. For the 'private_token' you need
        to configure a personal token access from your GitLab account.
        https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#creating-a-personal-access-token

        e.g. ~/.python-gitlab.cfg

    [global]
    default = default
    ssl_verify = true
    timeout = 5

    [default]
    url=https://git.vauxoo.com
    private_token=YOUR_TOKEN created from: https://git.vauxoo.com/profile/personal_access_tokens
    """

    def __init__(self):
        self.gitlab_api = gitlab.Gitlab.from_config("default", [CFG])
        self.access_level_code_name = {
            gitlab.const.GUEST_ACCESS: "guest",
            gitlab.const.REPORTER_ACCESS: "reporter",
            gitlab.const.DEVELOPER_ACCESS: "developer",
            gitlab.const.MAINTAINER_ACCESS: "maintainer",
            gitlab.const.OWNER_ACCESS: "owner",
        }
        self.access_level_name_code = {v: k for k, v in self.access_level_code_name.items()}
        self.pydir = os.path.abspath(os.path.dirname(__file__))
        self.mr_tmpl = os.path.join(self.pydir, "gitlab_mr_template")
        self.workdir = "gitlab_content"
        try:
            os.mkdir(self.workdir)
        except FileExistsError:  # pylint: disable=except-pass
            pass

    def get_mr_diff(self, project_name=None):
        project = self.gitlab_api.projects.get(project_name)
        # print(gl.projects.list())
        # print(project)
        mrs = project.mergerequests.list(state="opened")
        for mr in mrs:
            # diffs = mr.diffs.list()
            # print(diffs)
            # print(dir(mr))
            for change in mr.changes()["changes"]:
                print(change["diff"])
            # pylint: disable=pointless-string-statement
            """
            for diff in diffs:
                print(diff)
                print(dir(diff))
                print(diff.list())
                print(diff.short_print())
                print(diff.display(True))
            break
            """
        # print(mrs, len(mrs))c

    def get_members_grouped_by_access_level(self, group_id):
        group = self.gitlab_api.groups.get(group_id)
        members = group.members.list(all=True)
        get_members_by_access_level = defaultdict(list)
        for member in members:
            access_name = self.access_level_code_name[member.access_level]
            get_members_by_access_level[access_name].append(member)
        return get_members_by_access_level

    def delete_reporter_members(self, group_id):
        # pylint: disable=unreachable
        raise UserWarning(
            """Deleting a group_member will delete project_member too.
                          I mean, if a user was added to custom project_member but
                          it is deleted from group_member so the project_member will be deleted
                          Before to do it you will need get all users added manually to projects of the same group
                          e.g.
                           - vauxoo_group1: member_juan(Reporter)
                           - vauxoo_group1/project1: member_juan(Developer)

                           Running "vauxoo_group1.delete(member_juan)"
                           gitlab api will run "vauxoo_group1/project1.delete(member_juan)" too
                          """
        )
        reporter_members = self.get_members_grouped_by_access_level(group_id).get("reporter", [])
        for member in reporter_members:
            print("Deleting: <%s> %s" % (member.name, member.username))
            member.delete()

    def get_members_attributes(self, group_id):
        group = self.gitlab_api.groups.get(group_id)
        members = group.members.list(all=True)
        return [member.attributes for member in members]

    def get_basic_user_data(self, user):
        return {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "state": user.state,
            "email": user.email,
        }

    def get_users(self, email_domain=None):
        users = []
        for user in self.gitlab_api.users.list(all=True):
            if not email_domain:
                users.append(self.get_basic_user_data(user))
                continue
            if email_domain in user.email:
                users.append(self.get_basic_user_data(user))
        return users

    def project_mrs2csv(self, project_id=None):
        if not project_id:
            return

        task_label_pattern = re.compile(r"(task|t|vx|issue|i|us|hu)[# | -]?\d+", re.IGNORECASE)
        numbers_regex = re.compile(r"\d+")
        task_url_tmpl = "https://www.vauxoo.com/web#id=%s&model=%s&view_type=form"

        project = self.gitlab_api.projects.get(project_id)
        mrs = project.mergerequests.list(state="all", scope="all", all=True)

        csv_name = "%s_mrs_%s%s" % (project.name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), ".csv")
        with open(csv_name, "w+", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                [
                    "# de MR",
                    "URL del MR",
                    "Nombre de persona asignada",
                    "Título",
                    "Tarea",
                    "URL de la tarea",
                    "Estado",
                    "Etiquetas",
                    "Fecha de creación",
                    "Fecha de última actualización",
                    "Fecha de mezcla",
                ]
            )

            for mr in mrs:
                task_label = task_label_pattern.search(mr.title)
                task_id = ""
                task_url = ""

                if task_label:
                    task_id = task_label[0]
                    task_type = task_label[1]

                    if task_type in ("task", "t"):
                        model = "project.task"
                    else:
                        model = "helpdesk.ticket"

                    task_url = task_url_tmpl % (numbers_regex.search(task_id)[0], model)

                merge_date = mr.merged_at[:10] if mr.merged_at else ""

                writer.writerow(
                    [
                        mr.iid,
                        mr.web_url,
                        mr.author["name"],
                        mr.title,
                        task_id,
                        task_url,
                        mr.state,
                        mr.labels,
                        mr.created_at[:10],
                        mr.updated_at[:10],
                        merge_date,
                    ]
                )

    def look_for_filename(self, fname_regex, only_default_branch=False):
        non_ascii_pattern = re.compile(fname_regex)
        odoo_stable_branch = re.compile(r"^\d{2}\.0$")  # stable version of odoo
        for project in self.gitlab_api.projects.list(iterator=True):
            if project.path_with_namespace.split("/")[0].strip().endswith("-dev") or getattr(
                project, "forked_from_project", None
            ):
                # Filter "-dev" projects only stable ones and skip forked project
                continue
            branch_names = (
                [project.default_branch]
                if only_default_branch
                else [branch.name for branch in project.branches.list(get_all=True)]
            )
            for branch_name in branch_names:
                if not odoo_stable_branch.match(branch_name):
                    continue
                try:
                    project_file_objs = project.repository_tree(ref=branch_name, recursive=True, get_all=True)
                except gitlab.exceptions.GitlabGetError:
                    pass  # empty project
                for project_file_obj in project_file_objs:
                    if project_file_obj["type"] != "blob":
                        # only files
                        continue
                    path_name = project_file_obj["path"]
                    if non_ascii_pattern.search(path_name):
                        url = urllib.parse.quote(f"{project.path_with_namespace}/-/blob/{branch_name}/{path_name}")
                        print(f"{self.gitlab_api.url}/{url}")

    def get_project_files(self, fnames=None, branches=None):
        r"""Read the content of list of fnames and list of branches only
        stable projects and branches by default
        After generated the files you can use grep to find things
        e.g.
        grep -rn "INCLUDE\|EXCLUDE" vauxoo\_* jarsa\_* |sort | grep -v COVERAGE
        """
        if not fnames:
            fnames = ["variables.sh", ".gitlab-ci.yml"]
        if not branches:
            branches = ["17.0", "16.0", "15.0", "14.0", "13.0", "12.0"]
        print("Download files: %s\nfrom branches: %s\nto local path: ./%s" % (fnames, branches, self.workdir))
        for project in self.gitlab_api.projects.list(iterator=True):
            if project.path_with_namespace.split("/")[0].strip().endswith("-dev"):
                # Filter "-dev" projects only stable ones
                continue
            # TODO: Get file from branch (currently it is only from project)
            for branch in project.branches.list(iterator=True):
                # TODO: Use a regex here
                if branch.name not in branches:
                    # Filter only stable branches
                    continue
                for fname in fnames:
                    try:
                        branch_file = project.files.get(fname, branch.commit["id"])
                    except GitlabGetError:
                        continue
                    full_name = "%s_%s" % (project.path_with_namespace, branch.name)
                    for invalid_char in "@:/#.":
                        full_name = full_name.replace(invalid_char, "_")
                    full_name = os.path.join(self.workdir, "%s_%s" % (full_name, branch_file.file_name))
                    print("Wrote file %s" % full_name)
                    with open(full_name, "wb") as fobj:
                        fobj.write(branch_file.decode())

    def make_mr(  # pylint:disable=too-complex
        self,
        projects_branches,
        commit_msg,
        branch_dev_name,
        task_id=None,
        prefix_version=True,
        run_pre_commit_vauxoo=False,
    ):
        """Make a MR
        projects is a list of projects similar to ['vauxoo/addons@14.0']
        Use "gitlab_mr_template/" folder to make files changes in jinja2 format
        """
        # TODO: Add export BASE_IMAGE="vauxoo/odoo-{{version.replace('.')}}-image" if not exists or different
        # TODO: py.warnings for 14.0  # Add log-handler to silent py.warnings
        commit_msg = commit_msg.strip()
        title, _newline, description = commit_msg.partition("\n")
        description = description.strip()
        project_branches_dict = defaultdict(set)
        for project_branch in projects_branches:
            try:
                project_str, branch_str = project_branch.lower().strip().split("@")
            except ValueError:
                raise UserWarning("You need to use the format ['OWNER/PROJECT@BRANCH']")
            project_branches_dict[project_str.strip()].add(branch_str.strip())
        mrs = []
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(self.mr_tmpl, branch_dev_name)), autoescape=True
        )
        for project_str, branches_str in project_branches_dict.items():
            print("Processing project %s" % project_str)
            project = self.gitlab_api.projects.get(project_str)
            project_name = project.path_with_namespace.lower().strip()
            project_dev_str = project_str.replace("/", "-dev/", 1)
            try:
                project_dev = self.gitlab_api.projects.get(project_dev_str)
            except GitlabGetError:
                print("Project %s has no -dev branch, using same project to push dev branch" % project_name)
                project_dev = project
            for branch_str in branches_str:
                branch = project.branches.get(branch_str)
                custom_branch_dev_name = "%s-%s" % (branch.name, branch_dev_name)
                try:
                    branch_dev = project_dev.branches.get(custom_branch_dev_name)
                    branch_dev.delete()
                except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
                    pass
                branch_dev = project_dev.branches.create(
                    {"branch": custom_branch_dev_name, "ref": branch.commit["id"]}
                )
                with tempfile.TemporaryDirectory() as tmp_dir:
                    git_work_tree = os.path.join(tmp_dir, "gitlab")
                    git_cmd = [
                        "git",
                        "--git-dir=%s" % os.path.join(git_work_tree, ".git"),
                        "--work-tree=%s" % git_work_tree,
                    ]
                    try:
                        cmd = [
                            "git",
                            "clone",
                            "--single-branch",
                            "--dept=1",
                            "-b",
                            branch_dev.name,
                            project_dev.ssh_url_to_repo,
                            git_work_tree,
                        ]
                        subprocess.check_call(cmd)
                        tmpl_data = {}
                        tmpl_data["modules"] = [
                            module
                            for module in os.listdir(git_work_tree)
                            if os.path.isfile(os.path.join(git_work_tree, module, "__manifest__.py"))
                        ]
                        if not tmpl_data["modules"]:
                            print("MR creating skipped %s@%s no modules" % (project_name, branch.name))
                            continue
                        tmpl_data["project"] = project_name.split("/")[1]
                        tmpl_data["version"] = branch.name
                        for fname_tmpl in self.jinja_env.list_templates():
                            try:
                                with open(os.path.join(git_work_tree, fname_tmpl)) as sf_obj:
                                    tmpl_data["self_file"] = sf_obj.read()
                            except BaseException:
                                tmpl_data["self_file"] = ""
                            tmpl = self.jinja_env.get_template(fname_tmpl)
                            content = tmpl.render(tmpl_data).strip("\n") + "\n"
                            if len(content) == 1 and content == "\n":
                                content = ""
                            fname_out = os.path.join(git_work_tree, fname_tmpl)
                            os.makedirs(os.path.dirname(fname_out), exist_ok=True)
                            with open(fname_out, "w") as fobj:
                                fobj.write(content)
                            cmd = git_cmd + ["add", fname_tmpl]
                            subprocess.check_call(cmd)
                        if run_pre_commit_vauxoo:
                            if not pcv_cli:
                                raise ValueError("Please, install pip install pre-commit-vauxoo")
                            # Use py3.8.10 to match with dockerv image
                            with chdir(git_work_tree):
                                runner = CliRunner()
                                runner.invoke(pcv_cli.main, ["-t", "fix"])
                                # Call 2 times to fix conflicts with multiple autofixes
                                runner.invoke(pcv_cli.main, ["-t", "fix"])
                        git_cmd_diff = git_cmd + ["--no-pager", "diff", "--no-ext-diff", "--name-only"]
                        diff = subprocess.check_output(git_cmd_diff).strip(b"\n ")[:1]
                        diff += subprocess.check_output(git_cmd_diff + ["--cached"]).strip(b"\n ")[:1]
                        if not diff:
                            branch_dev.delete()
                            print("Skip: diff empty")
                            continue
                        # import pdb;pdb.set_trace()
                        cmd = git_cmd + ["commit", "-am", commit_msg]
                        subprocess.check_call(cmd)
                        cmd = git_cmd + ["push", "origin", "-f", custom_branch_dev_name]
                        subprocess.check_call(cmd)
                        mr_title = "%s - %s" % (branch.name, title) if prefix_version else title
                        if task_id:
                            mr_title += " T#%s" % task_id
                        mr = project_dev.mergerequests.create(
                            {
                                "target_project_id": project.id,
                                "source_branch": branch_dev.name,
                                "target_branch": branch.name,
                                "title": mr_title,
                                "description": description,
                                "remove_source_branch": True,
                            }
                        )
                        print(mr.web_url)
                        mrs.append(mr.web_url)
                    except subprocess.CalledProcessError:
                        print("MR creating error %s@%s Last command: %s" % (project_name, branch.name, " ".join(cmd)))
                    except BaseException as e:
                        print("MR creating error %s@%s err: %s" % (project_name, branch.name, e))
        return mrs

    def get_pipeline_artifacts(self, group, branches, job_names, artifacts_fname="artifacts.zip"):
        """Download and unzip artifacts for group/project"""
        group = self.gitlab_api.groups.get(group)
        for project_group in group.projects.list(iterator=True):
            project = self.gitlab_api.projects.get(project_group.id)
            project_name = project.path_with_namespace.replace("/", "_")
            visited = set()
            branches2work = set()
            for branch in branches:
                try:
                    project.branches.get(branch)
                    branches2work.add(branch)
                except gitlab.exceptions.GitlabGetError:
                    continue
            if not branches2work:
                print("Not branches to work found %s" % project_name)
                continue
            for job in project.jobs.list(iterator=True):
                if not branches2work - {branch for _, _, branch in visited}:
                    print("All branches were processed")
                    break
                if job.ref not in branches or job.name not in job_names:
                    continue
                artifact_key = (project_name, job.name, job.ref)
                if artifact_key in visited:
                    # TODO: Get the last job of a particular branch
                    continue
                fname_base = "_".join(artifact_key + (str(job.id),)).replace(".", "_")
                dirname = os.path.join(self.workdir, fname_base)
                fname = os.path.join(dirname, artifacts_fname)
                print("\nProcessing job: %s from %s" % (fname, job.web_url))
                if os.path.isdir(dirname):
                    print("...artifacts already downloaded")
                    visited.add(artifact_key)
                    continue
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        fname_tmp = os.path.join(tmp_dir, os.path.basename(fname))
                        with open(fname_tmp, "wb") as fartifact:
                            project.artifacts.download(
                                ref_name=job.ref,
                                job=job.name,
                                artifact_path=artifacts_fname,
                                streamed=True,
                                action=fartifact.write,
                            )
                        if os.stat(fname_tmp).st_size == 0:
                            raise UserWarning("Empty file")
                        shutil.copytree(tmp_dir, dirname)
                        print("writed %s" % fname)
                except (gitlab.exceptions.GitlabGetError, UserWarning) as gle:
                    print("Gitlab error %s: %s" % (fname, gle))
                    continue
                visited.add(artifact_key)
        print("Now you can run the following command to unzip all the files: ")
        print("find %s -name '*.zip' -type f -exec sh -c 'unzip -od `dirname {}` {} \"*odoo.log\"' ';'" % self.workdir)
