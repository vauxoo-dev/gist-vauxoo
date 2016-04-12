#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import click
import csv
import re
import ConfigParser
import requests
import json
from premailer import transform
from jinja2 import Environment, FileSystemLoader
from subprocess import check_output, STDOUT
from os.path import join
from os.path import dirname
from os.path import expanduser

__version__ = '1.0.0'

'''
Hacking:

If you improve this snnipet please set a new number of version in your PR.

TODO::

    * Use this as input file::

        http://docs.aws.amazon.com/cli/latest/userguide/generate-cli-skeleton.html
'''


goes_out = []
PROFILE = 'default'


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version: %s' % __version__)
    ctx.exit()


def call_command(command):
    try:
        # dear future me this join is not correct FIXME
        return check_output(' '.join(command), stderr=STDOUT, shell=True)
    except Exception, e:
        return e.output


def list_users(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version: %s' % __version__)
    return call_command(['aws', 'iam', 'list-users', '--profile', PROFILE])


def shell_check(func):
    def special_match(strg, search=re.compile(r'[^a-z0-9.]').search):
        assert isinstance(strg, str), 'Your csv must have a login column'
        assert bool(search(strg)), 'Invalid Login no special chars allowed'
        return func(strg)
    return special_match


@shell_check
def create_key(login):
    return call_command(['aws', 'iam', 'create-access-key', '--user-name',
                         login, '--profile', PROFILE])


@shell_check
def create_user(login):
    # TODO:
    # This is a little insecure but as this is out first run fix in the next
    return call_command(['aws', 'iam', 'create-user', '--user-name', login,
                         '--profile', PROFILE])


def add_group(login, group='files'):
    return call_command(['aws', 'iam', 'add-user-to-group', '--user-name',
                         login, '--group-name', group, '--profile', PROFILE])


def send_amazon(element, group='files'):
    login = element.get('login')
    click.echo('--- Working on %s ' % login)
    res = {
        'user': create_user(login),
        'group': add_group(login, group),
        'key': create_key(login)
    }
    click.echo('--- Ready on %s ' % login)
    return res


def create_users(in_file, group='files'):
    click.echo('Creating from %s' % in_file.name)
    spamreader = csv.DictReader(in_file, delimiter=',', quotechar='"')
    for row in spamreader:
        created = send_amazon(row, group)
        sent = send_message(created)
        click.echo(sent)


def send_message(data, mailgun_profile='sandbox'):
    def read_config_mailgun(section):
        config = ConfigParser.ConfigParser()
        config.read([expanduser('~/.config/mailgun.ini')])
        api_key = config.get(section, 'api_key')
        domain = config.get(section, 'domain')
        email_from = config.get(section, 'email_from')
        template = config.get(section, 'template')
        return (api_key, domain, email_from, template)

    def send_simple_message(api_key, domain, email_from, subject, email_to,
                            body, text=''):
        url = "https://api.mailgun.net/v3/{domain}/messages".format(domain=domain)  # noqa
        click.echo(url)
        data = {
                "from": email_from,
                "to": email_to,
                "subject": subject,
                "html": body,
                "text": 'hello',
            }
        click.echo(data)
        return requests.post(
            url,
            auth=("api", api_key),
            data=data)
    env_vars = read_config_mailgun(mailgun_profile)
    loader = FileSystemLoader(searchpath=join(dirname(__file__), 'templates'))
    env = Environment(loader=loader)
    template = env.get_template(env_vars[3])
    subject = 'VXScreenshots: Your Amazon S3 user has been created'
    sent = 'If you read this message was not sent'
    try:
        user = json.loads(data.get('user'))
        key = json.loads(data.get('key'))
        click.echo('User Dict')
        click.echo(user)
        html = transform(template.render(info={
                                       'user': user,
                                       'key': key,
                                       }))
        sent = send_simple_message(env_vars[0], env_vars[1], env_vars[2],
                                   subject,
                                   [user[u'User'][u'UserName']], html)
        click.echo(sent.text)
    except Exception, e:
        click.echo('Error sending:')
        click.echo(data.get('user'))
        click.echo(data.get('key'))
        click.echo(e.message)
        return False
    return sent.status_code == requests.codes.ok

#    return requests.post(
#           "https://api.mailgun.net/v3/%s/messages" % domain,
#           auth=("api", api_key),
#           data=data_dict)


@click.command()
@click.argument('names', nargs=-1)
@click.option('--i', type=click.File('rb'))
@click.option('--p', default='default', help='Local Amazon User Profile')
@click.option('--g', help='Group to assign to')
@click.option('--l', is_flag=True, callback=list_users,
              expose_value=False, is_eager=True, help='List users on amazon')
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show version and exit')
def main(names, i=None, p=None, n=None, g=None):
    '''Simple cli interface to create and set a group to an user in amazon in a
    documented manner and importing them from a csv file.:

    \b
    BEFORE USE THIS SCRIPT:
    -----------------------

    In order to send emails properly you need to copy the file
    templates/mailgun.ini into the .config folder on your user home.

    Read the doc of mailgun to understand the parameters.:

    https://documentation.mailgun.com/quickstart-sending.html

    Remember configure a different user before do this which allow create
    users::

    \b
        aws configure --profile user2

    Remember you can set the default in your sesion or use the -p parameter::

    \b
        export AWS_DEFAULT_PROFILE=user2

    In Amazon you need to create a group for this user with the ability of
    create
    and edit users.::

    http://screenshots.vauxoo.com/oem/7a49ce-1090x269.png

    Managed Policies that do the job::

    \b
        IAMFullAccess
        IAMUserSSHKeys

    Example of usage importing from csv::

    \b
        $ ./amazon_create_users.py --i res.users.csv  --p user2

    Save Keys in files::

        $ ./amazon_create_users.py --i res.users.csv  --p user2 > file_to_save.json

    Example of a csv file::

    \b
    "id","login"
    "yourownidentifier","username"

    You can list users also::

        \b
        $ ./amazon_create_users.py --l

        \b
        $ ./amazon_create_users.py --l > file_to_save.json

    The csv file just need to have a column called `login`::

    '''
    global PROFILE
    if p is not None:
        PROFILE = p
    click.echo(names)
    if i:
        click.echo('Reading %s' % i.name)
        if g is None:
            g = 'files'
        create_users(i, g)


if __name__ == '__main__':
    main()
