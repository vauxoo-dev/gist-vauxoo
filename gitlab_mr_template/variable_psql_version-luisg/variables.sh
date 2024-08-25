{%- for line in self_file.splitlines() %}
{{ line.replace('export PSQL_VERSION="14"', 'export PSQL_VERSION="15"') | safe }}
{%- endfor %}
