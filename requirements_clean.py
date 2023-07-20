import click

import re


@click.command()
@click.option('--project-requirements-path', help='Project requirements.txt')
@click.option('--odoo-requirements-path', help='Odoo requirements.txt file path', default="/home/odoo/instance/odoo/requirements.txt", show_default=True)
@click.option('--full-requirements-path', help='DeployV full_requirements.txt file path', default="/home/odoo/full_requirements.txt", show_default=True)
def clean_requirements(**kwargs):
    odoo_requirements_path = kwargs.get("odoo_requirements_path")
    project_requirements_path = kwargs.get("project_requirements_path")
    full_requirements_path = kwargs.get("full_requirements_path")

    with open(odoo_requirements_path) as f_odoo_requirements, open(project_requirements_path) as f_project_requirements, open(full_requirements_path) as f_full_requirements:
        
        full_requirements_packages = get_packages(f_full_requirements)

        project_requirements_packages = get_packages(f_project_requirements)

        odoo_requirements_packages = get_packages(f_odoo_requirements)

        missing_exclude = full_requirements_packages - odoo_requirements_packages - project_requirements_packages
        print("missing_exclude", missing_exclude)


def get_packages(lines):
    split_re = re.compile(r'[<>=#]')
    packages = set()
    for line in lines:
        package = split_re.split(line)[0].strip()
        if not package:
            continue
        packages.add(package)
    return packages


if __name__ == '__main__':
    clean_requirements()
