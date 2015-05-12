import itertools
import os
import re
import stat
import types
import yaml


class travis(object):

    def __init__(self, fname_travis_yml, fname_dockerfile):
        f_travis_yml = open(fname_travis_yml, "r")
        self.travis_data = yaml.load(f_travis_yml)
        self.travis2docker_section = [
            ('env', 'env'),
            ('install', 'run'),
            ('script', 'run'),
        ]
        self.travis2docker_section_dict = dict(self.travis2docker_section)
        self.fname_dockerfile = fname_dockerfile
        env_regex_str = r"(?P<var>[\w]*)[ ]*[\=][ ]*[\"\']{0,1}" + \
            r"(?P<value>[\w\.\-\_/\$\{\}\:]*)[\"\']{0,1}"
        export_regex_str = r"(?P<export>export|EXPORT)( )+" + env_regex_str
        self.env_regex = re.compile(env_regex_str, re.M)
        self.export_regex = re.compile(export_regex_str, re.M)
        self.extra_env_from_run = ""

    def get_travis_section(self, section):
        section_type = self.travis2docker_section_dict.get(section, False)
        if not section_type:
            return None
        section_data = self.travis_data[section]
        if isinstance(section_data, basestring):
            section_data = [section_data]
        job_method = getattr(self, 'get_travis2docker_' + section_type)
        return job_method(section_data)

    def get_travis2docker_run(self, section_data):
        docker_run = ''
        for line in section_data:
            for dummy, dummy, var, value in self.export_regex.findall(line):
                self.extra_env_from_run += "\nexport %s=%s" % (var, value)
            docker_run += '\n' + line
        return docker_run

    def get_travis2docker_env(self, section_data):
        for line in section_data:
            docker_env = ""
            for var, value in self.env_regex.findall(line):
                docker_env += "\nexport %s=%s" % (var, value)
            yield docker_env

    def get_default_cmd(self):
        cmd = "\nexport TRAVIS_BUILD_DIR=/root/myproject" + \
              "\ngit clone --single-branch git@github.com:Vauxoo/odoo-mexico-v2.git -b ${VERSION} ${TRAVIS_BUILD_DIR}"
        return cmd

    def get_travis2docker(self):
        travis2docker_cmd_static_str = ""
        travis2docker_cmd_iter_list = []
        for travis_section, dummy in self.travis2docker_section:
            travis2docker_section = self.get_travis_section(travis_section)
            if isinstance(travis2docker_section, types.GeneratorType):
                travis2docker_cmd_iter_list.append([
                    item_iter for item_iter in travis2docker_section
                ])
            elif isinstance(travis2docker_section, basestring):
                travis2docker_cmd_static_str += travis2docker_section + "\n"
        count = 1
        for item in itertools.product(*travis2docker_cmd_iter_list):
            fname = self.fname_dockerfile + str(count) + ".sh"
            with open(fname, "w") as fdockerfile:
                fdockerfile.write(
                    item[0] + "\n" +
                    self.get_default_cmd() + "\n" +
                    # extra environment variables if you split section
                    #   in many files cmd
                    # self.extra_env_from_run + "\n" +
                    travis2docker_cmd_static_str
                )
            st = os.stat(fname)
            os.chmod(fname, st.st_mode | stat.S_IEXEC)
            count += 1


if __name__ == '__main__':
    FNAME_TRAVIS_YML2 = "/Users/moylop260/openerp/instancias/" + \
        "odoo_git_clone/community-addons/odoo-mexico-v2/.travis.yml"
    FNAME_DOCKERFILE2 = "./borrar/cmd.sh"
    TRAVIS_OBJ = travis(FNAME_TRAVIS_YML2, FNAME_DOCKERFILE2)
    TRAVIS_OBJ.get_travis2docker()
    #  docker run -it -v ~/.ssh:/root/.ssh -v ./borrar:~/root/borrar
