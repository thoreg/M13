# -*- coding: utf-8 -*-
"""

# Example to update wheels for a topc branch:
fab update_wheels:branch=foo-bar

# Deploy topic branch
fab deploy:branch=foo-bar

To be able to build lxml the following packages need to be installed:

apt-get install libxml2-dev libxslt1-dev python-dev

"""
import os
import random
import string
import sys
from contextlib import contextmanager
from datetime import datetime

from fabric.api import cd, env, execute, hide, local, prefix, roles, run, sudo, task

ENVIRONMENT = 'live'
PROJECT_NAME = 'm13'
PYTHON_VERSION = '3.4.2'
REPOSITORY = 'git@github.com:thoreg/m13.git'
SETTINGS = 'm13.settings'
LIVE_SERVER = "m13stats"  # defined in .ssh/config
WHEELS_DIR = os.path.join(os.environ['M13_SERVER_PATH'], 'wheels')


env.shell = "/bin/bash -l -i -c"
env.project_src_dir = os.path.dirname(__file__)
env.no_agent = True
env.use_ssh_config = True
env.always_use_pty = True

env.roledefs = {
    'app': [LIVE_SERVER],
}

env.environment_dir = os.path.join(os.environ['M13_SERVER_PATH'], ENVIRONMENT)
env.srv_dir = os.path.join(env.environment_dir, 'versions')
env.envs_dir = os.path.join(os.environ['REMOTE_PYENV_ROOT'], 'versions')


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@contextmanager
def in_virtualenv(name):
    with prefix('pyenv activate {}'.format(name)):
        yield


@contextmanager
def silence():
    with hide('running', 'stdout', 'stderr'):
        yield


@task
def deploy(branch='master'):
    flake8()

    make_tag()

    appb(create_environment, branch)
    app(bower_install)
    app(collect_static)
    # app(compile_messages)
    app(update_symlinks)

    app(restart_server)

    app(cleanup)


def get_versions_to_cleanup():
    versions = run('ls {}'.format(env.srv_dir), shell=False)
    versions = sorted(versions.split(), reverse=True)
    versions_to_remove = versions[5:]

    return versions_to_remove


def cleanup_versions(versions):
    for version in versions:
        versions = run('rm -rf {}'.format(os.path.join(env.srv_dir, version)), shell=False)


def cleanup_virtual_envs(versions):
    for version in versions:
        run('pyenv uninstall -f {}'.format(version))


def cleanup():
    versions = get_versions_to_cleanup()
    if versions:
        cleanup_versions(versions)
        cleanup_virtual_envs(versions)


def app(task):
    execute(task, hosts=env.roledefs['app'])


def appb(task, branch):
    execute(task, branch, hosts=env.roledefs['app'])


def ok():
    print("\n[ OK ]\n\n")


def exit_on_fail():
    print("\n[ !!! ]")
    sys.exit(1)


@task
def flake8():
    local("flake8")
    ok()


@task
def make_tag():
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    tag_name = "m13-stats-deployed-%s" % now
    local("git tag %s" % tag_name)
    local("git push origin")
    local("git push origin --tags")
    ok()


def get_tag_name():
    return local("git tag --list | tail -n 1", capture=True)


@task
@roles('app')
def update_wheels(branch='master'):
    path = os.path.join('/tmp/update_wheels_repo')
    run('rm -rf {}'.format(path))
    run('mkdir -p {}'.format(path))
    print("Path is {}".format(path))
    print("Branch is {}".format(branch))

    with cd(path):
        print("Clone repository ...")
        with silence():
            run('git clone {}'.format(REPOSITORY))
        ok()

        with cd(os.path.join(path, PROJECT_NAME)):
            tag = get_tag_name()
            run('git checkout {}'.format(tag))

            random_pyenv_name = id_generator()
            run('pyenv virtualenv {} {}'.format(PYTHON_VERSION, random_pyenv_name))
            with in_virtualenv(random_pyenv_name):
                run('pip install -U pip')
                run('pip install -U wheel')
                run('pip wheel --wheel-dir={} -r requirements.txt'.format(WHEELS_DIR))
                ok()

                run('pyenv deactivate')
                ok()

            run('pyenv uninstall -f {}'.format(random_pyenv_name))
            ok()


@task
@roles('app')
def create_environment(branch):

    tagname = get_tag_name()
    run('pyenv virtualenv {} {}'.format(PYTHON_VERSION, tagname))
    print("Create new environment - {}".format(tagname))
    print("Branch: {}".format(branch))

    next_version_path = os.path.join(env.srv_dir, tagname)
    run('mkdir -p {}'.format(next_version_path))
    with cd(next_version_path):
        print("Clone repository ...")
        with silence():
            run('git clone {}'.format(REPOSITORY))

    project_path = os.path.join(next_version_path, PROJECT_NAME)
    print("Project path is {}".format(project_path))
    with silence():
        with in_virtualenv(tagname):
            with cd(project_path):
                if branch != 'master':
                    run('git checkout -b {} origin/{}'.format(branch, branch))
                run('pip install --no-index --find-links={} -r requirements.txt'.format(WHEELS_DIR))
    ok()


@task
@roles('app')
def bower_install():
    tagname = get_tag_name()
    print("Bower install ...")
    with silence():
        with in_virtualenv(tagname):
            project_path = os.path.join(env.srv_dir, tagname, PROJECT_NAME)
            with cd(project_path):
                run('python manage.py bower_install --settings={}'.format(SETTINGS))
    ok()


@task
@roles('app')
def collect_static():
    tagname = get_tag_name()
    print("Collect static files ...")
    with silence():
        with in_virtualenv(tagname):
            project_path = os.path.join(env.srv_dir, tagname, PROJECT_NAME)
            with cd(project_path):
                run('python manage.py collectstatic --noinput --settings={}'.format(SETTINGS))
    ok()


@task
@roles('app')
def compile_messages():
    tagname = get_tag_name()
    print("Compile messages ...")
    with silence():
        with in_virtualenv(tagname):
            project_path = os.path.join(env.srv_dir, tagname, PROJECT_NAME)
            with cd(project_path):
                run('python manage.py compilemessages --settings={}'.format(SETTINGS))
    ok()


@roles('app')
def update_symlinks(tag=""):
    print("Updating symlinks")
    if not tag:
        tag = get_tag_name()

    print("Get active environment ...")
    current_tag = get_active_environment()

    print("Save the last live link")
    with prefix("ln -sfn `readlink live` last"):
        with cd(env.environment_dir):
            result1 = run("ln -sfn {} live".format(os.path.join(env.srv_dir, tag)),
                          warn_only=True)

        with cd(env.envs_dir):
            result2 = run("ln -sfn {} {}".format(os.path.join(env.envs_dir, tag), ENVIRONMENT),
                          warn_only=True)

    if result1.failed or result2.failed:
        # revert to the previous settings
        with cd(env.environment_dir):
            run("ln -sfn {} live".format(os.path.join(env.srv_dir, current_tag)))

        with cd(env.envs_dir):
            run("ln -sfn {} {}".format(os.path.join(env.envs_dir, current_tag), ENVIRONMENT))

        exit_on_fail()
    else:
        ok()


@roles('app')
def restart_server():
    sudo("/etc/init.d/uwsgi restart", shell=False)
    sudo("/etc/init.d/nginx restart", shell=False)
    ok()


@roles('app')
def get_active_environment():
    print("-- in get_active_environment()")
    with cd(env.environment_dir):
        current_environment = run("readlink live")
        print("Current environment: {}".format(current_environment))
        return os.path.basename(current_environment)


@task
@roles('app')
def sync_local_db_with_live_db():
    """
    Get the live database to the local db for development.

    - Dump the live database on the remote server
    - Copy the dump file to the local
    - Insert the downloaded file and delete it

    """
    print("\nSync the local database with the live database ...")
    dump_name = '{}-m13-stats-db.sql'.format(datetime.now().strftime("%Y%m%dT%H%M"))
    params = {
        'db': os.environ['M13_DATABASE'],
        'dump_name': dump_name,
        'dump_path': os.path.join(env.environment_dir, 'dumps', dump_name),
        'localhost': '127.0.0.1',
        'port': '5666',
        'server': LIVE_SERVER,
        'user': os.environ['M13_DATABASE_USER'],
    }

    # Drop local db and create new
    local('psql -h {localhost} -c "DROP DATABASE {db}" postgres'.format(**params))
    local('psql -h {localhost} -c "CREATE DATABASE {db} WITH OWNER {user}" postgres'.format(**params))

    # Dump db on live
    run('pg_dump -h {localhost} -p {port} -U {user} {db} > {dump_path}'.format(**params))

    # Insert the live dump in local db
    local('scp {server}:{dump_path} .'.format(**params))
    local('psql -U {user} {db} < {dump_name}'.format(**params))
    local('rm {dump_name}'.format(**params))

    ok()
