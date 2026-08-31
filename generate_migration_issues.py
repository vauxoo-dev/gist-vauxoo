import argparse
import csv
import logging
import os

import github
import gitlab

# Define the version number
VERSION = "0.1"
GITLAB_CFG = os.path.expanduser("~/.python-gitlab.cfg")
os.environ["NETRC"] = "~/.python-github.netrc"

logging.basicConfig(level=logging.INFO)


def load_migrated_modules(input_file):
    if input_file is None:
        return None
    migrated_modules = []
    with open(input_file, newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        next(csv_reader)
        for row in csv_reader:
            migrated_modules.append(row[0].split(","))
    return migrated_modules


def load_unmigrated_modules(input_file):
    unmigrated_modules = []
    with open(input_file, newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            if len(row) == 5 and row[4] == "False":
                unmigrated_modules.append(row)
    return unmigrated_modules


def validate_github_repository_by_module(module, odoo_target_version, github_obj, limit_search="All"):
    limit_search = limit_search.split(",") if isinstance(limit_search, str) else limit_search
    # repo_url = None
    module_url = None
    was_migrated = None
    if "OCA" in limit_search:
        github_org = github_obj.get_organization("oca")
        github_repos = github_org.get_repos()
    elif "All" in limit_search:
        github_org = github_obj.get_organization("vauxoo")
        github_repos = github_org.get_repos()
    elif ["odoo", "enterprise"] == limit_search:
        query = ["repo:odoo/" + repo for repo in limit_search]
        query = " ".join(query)
        github_repos = github_obj.search_repositories(query=query)
    elif limit_search:
        query = ["repo:vauxoo/" + repo for repo in limit_search]
        query = " ".join(query)
        github_repos = github_obj.search_repositories(query=query)
    else:
        github_repos = []
    for repo in github_repos:
        try:
            if repo.name == "odoo":
                repo.get_contents("addons/" + module)
            else:
                repo.get_contents(module)
            # repo_url = "https://github.com/" + repo.full_name
            if repo.name == "odoo":
                module_url = (
                    "https://github.com/" + repo.full_name + "/tree/" + repo.default_branch + "/addons/" + module
                )
                manifest = repo.get_contents(
                    "addons/" + module + "/__manifest__.py", ref=odoo_target_version
                ).decoded_content.decode()
                module_url = (
                    "https://github.com/" + repo.full_name + "/tree/" + odoo_target_version + "/addons/" + module
                )
                was_migrated = True
            elif repo.name == "enterprise":
                module_url = "https://github.com/" + repo.full_name + "/tree/" + repo.default_branch + "/" + module
                manifest = repo.get_contents(
                    module + "/__manifest__.py", ref=odoo_target_version
                ).decoded_content.decode()
                module_url = "https://github.com/" + repo.full_name + "/tree/" + odoo_target_version + "/" + module
                was_migrated = True
            else:
                module_url = "https://github.com/" + repo.full_name + "/tree/" + repo.default_branch + "/" + module
                manifest = repo.get_contents(
                    module + "/__manifest__.py", ref=odoo_target_version
                ).decoded_content.decode()
                module_url = "https://github.com/" + repo.full_name + "/tree/" + odoo_target_version + "/" + module
                was_migrated = any(odoo_target_version in line for line in manifest.splitlines() if "version" in line)
            break
        except github.GithubException:
            continue
    if module_url and was_migrated is None:
        was_migrated = False
    return module_url, was_migrated


def validate_gitlab_repository_by_module(module, odoo_target_version, gitlab_obj, limit_search="All"):
    limit_search = limit_search.split(",") if isinstance(limit_search, str) else limit_search
    # repo_url = None
    module_url = None
    was_migrated = None
    if "All" in limit_search:
        projects = gitlab_obj.projects.list(get_all=True)
        for project in projects:
            if "-dev" not in project.namespace["name"] and "addons-vauxoo" not in project.name:
                try:
                    _ = project.files.get(file_path=module + "/__manifest__.py", ref=project.default_branch)
                    # repo_url = project.web_url
                    module_url = (
                        project.web_url + "/-/tree/" + project.default_branch + "/" + module + "?ref_type=heads"
                    )
                    manifest = (
                        project.files.get(file_path=module + "/__manifest__.py", ref=odoo_target_version)
                        .decode()
                        .decode("ascii")
                    )
                    module_url = project.web_url + "/-/tree/" + odoo_target_version + "/" + module + "?ref_type=heads"
                    was_migrated = any(
                        odoo_target_version in line for line in manifest.splitlines() if "version" in line
                    )
                    break
                except (gitlab.exceptions.GitlabGetError, AttributeError):
                    continue

    elif limit_search:
        for repository in limit_search:
            projects_subset = gitlab_obj.search(gitlab.const.SearchScope.PROJECTS, repository)
            for repo in projects_subset:
                if "-dev" not in repo["namespace"]["name"]:
                    proj = repo
            project = gitlab_obj.projects.get(proj["id"], lazy=True)
            try:
                _ = project.files.get(file_path=module, ref=project["default_branch"])
                # repo_url = project["web_url"]
                module_url = (
                    project["web_url"] + "/-/tree/" + project["default_branch"] + "/" + module + "?ref_type=heads"
                )
                manifest = (
                    project.files.get(file_path=module + "/__manifest__.py", ref=odoo_target_version)
                    .decode()
                    .decode("ascii")
                )
                module_url = project["web_url"] + "/-/tree/" + odoo_target_version + "/" + module + "?ref_type=heads"
                was_migrated = any(odoo_target_version in line for line in manifest.splitlines() if "version" in line)
                break
            except (gitlab.exceptions.GitlabGetError, AttributeError):
                continue

    if module_url and was_migrated is None:
        was_migrated = False
    return module_url, was_migrated


def validate_repository_by_module(module, odoo_target_version, gitlab_obj, github_obj, limit_search="All"):
    limit_search = limit_search.split(",") if isinstance(limit_search, str) else limit_search
    if limit_search in (["OCA"], ["odoo", "enterprise"]):
        repository_url, was_migrated = validate_github_repository_by_module(
            module, odoo_target_version, github_obj, limit_search=limit_search
        )
    elif limit_search:
        repository_url, was_migrated = validate_gitlab_repository_by_module(
            module, odoo_target_version, gitlab_obj, limit_search=limit_search
        )
        if not repository_url:
            repository_url, was_migrated = validate_github_repository_by_module(
                module, odoo_target_version, github_obj, limit_search=limit_search
            )
    else:
        repository_url = None
        was_migrated = None
    return repository_url, was_migrated


def search_in_vauxoo_migrated_modules(migrated_modules, module):
    module_url = None
    was_migrated = None
    for m_row in migrated_modules:
        _, _, m_name, m_module_url, m_state, m_new_name, m_new_module_url = m_row
        if module == m_name:
            module_url, was_migrated = m_module_url, m_state == "True"
        elif module == m_new_name:
            module_url, was_migrated = m_new_module_url, m_state == "True"
    return module_url, was_migrated


def search_in_repositories_by_module(
    authors, module, odoo_target_version, vauxoo_repositories, gitlab_obj, github_obj
):
    module_url = None
    was_migrated = None
    if "OCA" in authors:
        module_url, was_migrated = validate_repository_by_module(
            module, odoo_target_version, gitlab_obj, github_obj, limit_search="OCA"
        )
    elif "Odoo" in authors:
        module_url, was_migrated = validate_repository_by_module(
            module, odoo_target_version, gitlab_obj, github_obj, limit_search=["odoo", "enterprise"]
        )
    elif "Vauxoo" in authors:
        module_url, was_migrated = validate_repository_by_module(
            module,
            odoo_target_version,
            gitlab_obj,
            github_obj,
            limit_search=vauxoo_repositories.split(","),
        )
    else:
        module_url, was_migrated = "Third-party module", None
    return module_url, was_migrated


def process_csv(
    input_modules_csv_file,
    odoo_target_version,
    migrated_modules_csv_file=None,
    modules_status_csv_file="migrated_modules_output.csv",
    vauxoo_repositories="All",
):
    auth = github.Auth.NetrcAuth()
    github_obj = github.Github(auth=auth, retry=None)

    gitlab_obj = gitlab.Gitlab.from_config("default", [GITLAB_CFG])

    migrated_modules = load_migrated_modules(migrated_modules_csv_file)
    with open(input_modules_csv_file, newline="") as input_file:
        input_reader = csv.reader(input_file, delimiter=",")
        next(input_reader)
        with open(modules_status_csv_file, "w", newline="") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(["Level", "Name", "Authors", "Module URL", "Migrated"])
            for row in input_reader:
                level, module, authors = row
                if migrated_modules:
                    module_url, was_migrated = search_in_vauxoo_migrated_modules(migrated_modules, module)
                if not migrated_modules or not module_url:
                    try:
                        module_url, was_migrated = search_in_repositories_by_module(
                            authors, module, odoo_target_version, vauxoo_repositories, gitlab_obj, github_obj
                        )
                    except Exception as e:
                        logging.error(f"Error processing module {module}: {e}")
                        module_url, was_migrated = "Error", "Error"
                logging.info([level, module, authors, module_url, was_migrated])
                writer.writerow([level, module, authors, module_url, was_migrated])


def create_issues(
    modules_status_csv_file,
    vauxoo_task,
    gitlab_project,
    odoo_target_version,
):
    gitlab_obj = gitlab.Gitlab.from_config("default", [GITLAB_CFG])
    unmigrated_modules = load_unmigrated_modules(modules_status_csv_file)
    projects_subset = gitlab_obj.search(gitlab.const.SearchScope.PROJECTS, gitlab_project)
    for repository in projects_subset:
        if "-dev" not in repository["namespace"]["name"] and gitlab_project[0] == repository["name"]:
            project = repository
    issue_project = gitlab_obj.projects.get(project["id"], lazy=True)
    for module_info in unmigrated_modules:
        priority, name, _, module_url, _ = module_info
        issue_project.issues.create(
            {
                "title": f"[MIG] {name} to v{odoo_target_version} / Priority: {priority}",
                "description": f"Code: {module_url}/{name}\n\nTask: {vauxoo_task}",
            }
        )
        logging.info("Issue was created...")


def validate_gitlab_modules_by_project(project, odoo_version):
    modules_list = []
    if "-dev" not in project.namespace["name"] and "addons-vauxoo" not in project.name:
        # print([project.namespace["name"], project.name])
        try:
            files = project.repository_tree(get_all=True)
        except gitlab.exceptions.GitlabGetError:
            files = []
        for file in files:
            try:
                manifest = (
                    project.files.get(file_path=file["name"] + "/__manifest__.py", ref=odoo_version)
                    .decode()
                    .decode("utf-8")
                )
                # print([project.namespace["name"], project.name, file["name"]])
                module_url = project.web_url + "/-/tree/" + odoo_version + "/" + file["name"] + "?ref_type=heads"
                was_migrated = any(odoo_version in line for line in manifest.splitlines() if "version" in line)
                modules_list.append([project.namespace["name"], project.name, file["name"], module_url, was_migrated])
                logging.info([project.namespace["name"], project.name, file["name"], was_migrated])
            except (gitlab.exceptions.GitlabGetError, AttributeError):
                continue
    return modules_list


def create_migrated_modules_files(odoo_version, migrated_modules_csv_file):
    gitlab_obj = gitlab.Gitlab.from_config("default", [GITLAB_CFG])
    projects = gitlab_obj.projects.list(get_all=True)
    with open(migrated_modules_csv_file, "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Group", "Project", "Name", "Module URL", "Migrated", "New name", "New Module URL"])
        for project in projects:
            modules_list = validate_gitlab_modules_by_project(project, odoo_version)
            for module_row in modules_list:
                writer.writerow(module_row + [None, None])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="""
        Process the dependencies in the CSV file to obtain their migration status,
        and create migration issues related to the modules that have not yet been migrated.

        Usage examples:
        1)  create-full-target-status-file
                -otv    17.0
                -fts    full_target_status_17.csv

        2)  modules-status
                -md     module_priority_pulso-13-0.csv
                -fts    full_target_status_17.csv
                -ms     migrated_modules_output.csv
                -otv    17.0

        3)  create-issues
                -ms     migrated_modules_output.csv
                -vt     'https://www.vauxoo.com/web#id=63809&cids=1&model=project.task&view_type=form'
                -gp     typ
                -otv    17.0
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for project modules migration status
    import_parser = subparsers.add_parser("modules-status")
    import_parser.add_argument(
        "-md",
        "--modules_dependencies",
        type=str,
        help="Input module dependencies with priorities CSV file",
    )
    import_parser.add_argument(
        "-fts",
        "--full_target_status",
        nargs="?",
        default=None,
        const=None,
        type=str,
        help="Input full vauxoo modules status in target version CSV file",
    )
    import_parser.add_argument(
        "-ms",
        "--modules_status",
        nargs="?",
        default="migrated_modules_output.csv",  # Maybe validate if no output nedded, go to generate the issues
        const="migrated_modules_output.csv",
        type=str,
        help="Output module dependencies with priorities migration status CSV file",
    )
    import_parser.add_argument(
        "-vr",
        "--vauxoo_repositories",
        nargs="?",
        default="All",
        const="All",
        type=str,
        help="Vauxoo repositories where modules are search separated by commas. E.g. repo,repo2,repo3",
    )
    import_parser.add_argument(
        "-otv", "--odoo_target_version", nargs=1, type=str, help="Odoo target version. E.g. 16.0"
    )

    # Subparser for issues creation
    import_parser = subparsers.add_parser("create-issues")
    import_parser.add_argument(
        "-ms",
        "--modules_status",
        nargs="?",
        default="migrated_modules_output.csv",
        const="migrated_modules_output.csv",
        type=str,
        help="Input module dependencies with priorities migration status CSV file",
    )
    import_parser.add_argument("-vt", "--vauxoo_task", nargs=1, type=str, help="Vauxoo task link to add to the issue.")
    import_parser.add_argument(
        "-gp", "--gitlab_project", nargs=1, type=str, help="Gitlab project name where issues are going to be posted."
    )
    import_parser.add_argument(
        "-otv", "--odoo_target_version", nargs=1, type=str, help="Odoo target version. E.g. 16.0"
    )

    # Subparser for full vauxoo modules in target version status file creation
    import_parser = subparsers.add_parser("create-full-target-status-file")
    import_parser.add_argument(
        "-otv", "--odoo_target_version", nargs=1, type=str, help="Odoo target version. E.g. 16.0"
    )
    import_parser.add_argument(
        "-fts",
        "--full_target_status",
        nargs="?",
        default=None,
        const=None,
        type=str,
        help="Input full vauxoo modules status in target version CSV file",
    )

    parser.add_argument("--version", action="version", version="%(prog)s {}".format(VERSION))

    args = parser.parse_args()
    #import pdb; pdb.set_trace()
    #if "full_target_status" in args and args.full_target_status is None:
        #args.full_target_status = f"full_target_status_{args.odoo_target_version[0][:-2]}.csv"
    if args.command == "modules-status":
        process_csv(
            input_modules_csv_file=args.modules_dependencies,
            migrated_modules_csv_file=args.full_target_status,
            modules_status_csv_file=args.modules_status,
            vauxoo_repositories=args.vauxoo_repositories,
            odoo_target_version=args.odoo_target_version[0],
        )
    elif args.command == "create-issues":
        create_issues(
            modules_status_csv_file=args.modules_status,
            vauxoo_task=args.vauxoo_task,
            gitlab_project=args.gitlab_project,
            odoo_target_version=args.odoo_target_version[0],
        )

    elif args.command == "create-full-target-status-file":
        create_migrated_modules_files(
            odoo_version=args.odoo_target_version[0],
            migrated_modules_csv_file=args.full_target_status,
        )
    else:
        logging.error("Please provide a valid command.")
