export DOCKER_IMAGE_REPO="quay.io/vauxoo/nocustomers"
export MAIN_APP="{{modules[0]}}"
export CUSTOMER="{{project}}"
export PRECOMMIT_HOOKS_TYPE="all,-fix"
export TRAVIS_PYTHON_VERSION="3.8"{% for line in self_file.splitlines() %}{% if 'TRAVIS_PYTHON_VERSION' not in line %}
{{line}}{% endif %}{% endfor %}
