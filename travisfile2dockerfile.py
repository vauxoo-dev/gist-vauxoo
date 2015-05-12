import itertools
import os
import re
import stat
import types
import yaml


# TODO: Change name of class and variables to cmd
class travis(object):

    def __init__(self, fname_travis_yml, fname_dockerfile):
        """
        Method Constructor
        @fname_travis_yml: str name of file travis.yml to use.
        @fname_dockerfile: str name of file dockerfile to save.
        """
        f_travis_yml = open(fname_travis_yml, "r")
        self.travis_data = yaml.load(f_travis_yml)
        self.travis2docker_section = [
            ('python', 'python'),
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
        section_data = self.travis_data.get(section, "")
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

    def get_travis2docker_python(self, section_data):
        for line in section_data:
            yield "# TODO: Use python version: " + line

    def get_default_cmd(self):
        cmd = "\nexport TRAVIS_BUILD_DIR=/root/myproject" + \
              "\ngit clone --single-branch git@github.com:Vauxoo/vauxoo-applicant.git -b master ${TRAVIS_BUILD_DIR}"
        return cmd

    def get_travis2docker_iter(self):
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
        for item in itertools.product(*travis2docker_cmd_iter_list):
            yield item[0] + "\n" + \
                self.get_default_cmd() + "\n" + \
                travis2docker_cmd_static_str
            # extra environment variables if you split section
            #   in many files cmd
            # self.extra_env_from_run + "\n" + \

    def get_travis2docker(self):
        count = 1
        for cmd in self.get_travis2docker_iter():
            fname = self.fname_dockerfile + str(count) + ".sh"
            with open(fname, "w") as fdockerfile:
                fdockerfile.write(cmd)
            st = os.stat(fname)
            os.chmod(fname, st.st_mode | stat.S_IEXEC)
            count += 1


if __name__ == '__main__':
    # TODO: Use options to get this params
    FNAME_TRAVIS_YML2 = "/Users/moylop260/openerp/instancias/" + \
        "odoo_git_clone/community-addons/vauxoo-applicant/.travis.yml"
    FNAME_DOCKERFILE2 = "./borrar/cmd.sh"
    TRAVIS_OBJ = travis(FNAME_TRAVIS_YML2, FNAME_DOCKERFILE2)
    TRAVIS_OBJ.get_travis2docker()
    #print "docker run -it --name=borrar70 -v ~/borrar:/root/borrar -v ~/.ssh:/root/.ssh -v %s:/root/myproject vauxoo/odoo-80-image-shippable-auto /bin/sh -c /root/borrar/cmd.sh"%(FNAME_TRAVIS_YML2)

