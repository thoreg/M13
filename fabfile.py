"""
# -*- coding: utf-8 -*-
#
# Example to update wheels for a topc branch:
fab update_wheels:branch=foo-bar

# Deploy topic branch
fab deploy:branch=foo-bar

# Run tests
fab test

# Run tests and collect coverage data
fab test:with_coverage_report=1


"""
import os
import random
import string
import sys
from contextlib import contextmanager
from datetime import datetime

from fabric.api import (cd, env, execute, hide, local, prefix, roles, run,
                        sudo, task)

REPOSITORY = 'git@github.com:thoreg/m13.git'
PROJECT_NAME = 'm13'
PYTHON_VERSION = '3.4.2'

env.shell = "/bin/bash -l -i -c"
env.project_src_dir = os.path.dirname(__file__)
env.no_agent = True
env.use_ssh_config = True
env.always_use_pty = True

env.roledefs = {
    'app': ['d186'],
}

env.app_server = 'd186'

ENVIRONMENT = 'live'
env.environment_dir = os.path.join(os.environ['M13_SERVER_PATH'], ENVIRONMENT)
env.versions_dir = os.path.join(env.environment_dir, 'versions')
env.envs_dir = os.path.join(env.environment_dir, 'envs')

# SETTINGS = 'config.settings.staging'
SETTINGS = 'm13.settings'

WHEELS_DIR = os.path.join(os.environ['M13_SERVER_PATH'], 'wheels')


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@contextmanager
def in_virtualenv(name):
    with prefix('pyenv activate {}'.format(name)):
        yield


@contextmanager
def in_versions_dir():
    with cd(env.versions_dir):
        yield


@contextmanager
def silence():
    with hide('running', 'stdout', 'stderr'):
        yield


@task
def deploy(branch='master'):
    flake8()
    # check_working_directory_clean()

    make_tag()

    appb(create_environment, branch)
    app(collect_static)
    app(compile_messages)
    app(update_symlinks)

    app(restart_server)


@task
def cleanup():
    app(cleanup_environment)
    remove_local_tarfiles()


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
def sanity_check():
    check_current_branch_is(ENVIRONMENT)
    check_working_directory_clean()


@task
def check_working_directory_clean():
    cmd = 'git status --porcelain'
    result = local(cmd, capture=True)
    if len(result) > 0:
        print("\n{}".format(result))
        print("\n\tPlease clean the working directory before deploying. The command\n")
        print("\t$ git reset --hard live")
        print("\twill reset the working directory to the last deployed state.\n")
        print("\t$ git clean --dry-run")
        print("\twill remove untracked files from the working directory, if you\n")
        print("\tremove --dry-run.")
        exit_on_fail()
    else:
        print("Working directory clean.")
        ok()


@task
def check_current_branch_is(branch_name):
    """
    Verify that the current branch is 'branch_name'

    """
    if local("git symbolic-ref HEAD", capture=True) != 'refs/heads/{}'.format(branch_name):
        print("\n\tThe current branch is not the branch '{}'.".format(branch_name))
        print("\tYou can switch to the '{}' branch with the command".format(branch_name))
        print("\n\t$ git checkout {}\n".format(branch_name))
        exit_on_fail()
    else:
        print("On branch '{}'.".format(branch_name))
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

    next_version_path = os.path.join(env.versions_dir, tagname)
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
def collect_static():
    tagname = get_tag_name()
    print("Collect static files ...")
    with silence():
        with in_virtualenv(tagname):
            project_path = os.path.join(env.versions_dir, tagname, PROJECT_NAME)
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
            project_path = os.path.join(env.versions_dir, tagname, PROJECT_NAME)
            with cd(project_path):
                run('python manage.py compilemessages --settings={}'.format(SETTINGS))
    ok()


@task
@roles('app')
def cleanup_environment():
    """
    Keep only the last 5 deployed environments.

    """
    print("Cleaning up")
    with cd(env.versions_dir):
        tags = run("ls -1dr deployed-*").split()
        if len(tags) > 10:
            tags = tags[5:]
            for tag in tags:
                print("Removing Tag/Virtualenv {}".format(tag))
                tarfile = env.filename_tar % tag
                run("rm -rf {} {}".format(tarfile, tag), warn_only=True)
                run("rmvirtualenv {}".format(tag), warn_only=True)
                ok()


@task
def remove_local_tarfiles():
    local("rm -vf {}".format(os.path.join('..', '{}_deployed*.tar.gz'.format(PROJECT_NAME))))


@task
@roles('app')
def update_symlinks(tag=""):
    print("Updating symlinks")
    if not tag:
        tag = get_tag_name()

    check_if_remote_environment_exists(tag)

    current_tag = get_active_environment()

    print("Save the last live link")
    with prefix("ln -sfn `readlink live` last"):
        with cd(env.environment_dir):
            result1 = run("ln -sfn {} live".format(os.path.join(env.versions_dir, tag)),
                          warn_only=True)

        with cd(env.envs_dir):
            result2 = run("ln -sfn {} {}".format(os.path.join(env.envs_dir, tag), ENVIRONMENT),
                          warn_only=True)

    if result1.failed or result2.failed:
        # revert to the previous settings
        with cd(env.environment_dir):
            run("ln -sfn {} live".format(os.path.join(env.versions_dir, current_tag)))

        with cd(env.envs_dir):
            run("ln -sfn {} {}".format(os.path.join(env.envs_dir, current_tag), ENVIRONMENT))

        exit_on_fail()
    else:
        ok()


@task
@roles('app')
def check_if_remote_environment_exists(tagname):
    check_if_remote_tagname_exists(tagname)
    check_if_remote_virtualenv_exists(tagname)


def check_if_remote_tagname_exists(tagname):
    with cd(env.versions_dir):
        run("ls -d %s" % tagname)


def check_if_remote_virtualenv_exists(tagname):
    with cd(env.envs_dir):
        run("ls -d %s" % tagname)


@task
@roles('app')
def restart_server():
    sudo("/etc/init.d/supervisor restart", shell=False)
    sudo("/etc/init.d/nginx restart", shell=False)


def get_active_environment():
    with cd(env.environment_dir):
        with silence():
            current_environment = run("readlink live")

        current_environment = run("readlink live")
        print("Current environment: {}".format(current_environment))
        return os.path.basename(current_environment)


def get_last_active_environment():
    with cd(env.home_dir):
        with silence():
            tag = run("readlink last")

        return os.path.basename(tag)


@task
def print_the_latest_twenty_tags():
    local('git tag --list | sort -r | head -20')


@task
def rollback(tag):
    update_symlinks(tag)


@task
def sync_local_db_with_staging_db():
    print("\nSync the local database with the staging database ...")
    params = {
        'staging': '192.168.178.65',
        'localhost': '127.0.0.1',
        'user': 'djangocms',
        'db': 'djangocms_staging',
    }

    # The next two lines work on LinuX (Ubuntu)
    # local('sudo -u postgres psql -c "DROP DATABASE {db}"'.format(**params))
    # local('sudo -u postgres psql -c "CREATE DATABASE {db} WITH OWNER {user}"'.format(**params))

    # The next two lines work on MacOSX (postgresql installed via brew)
    local('psql -c "DROP DATABASE {db}" postgres'.format(**params))
    local('psql -c "CREATE DATABASE {db} WITH OWNER {user}" postgres'.format(**params))
    local('pg_dump --verbose -h {staging} -U {user} {db} | psql -h {localhost} -U {user} {db}'.format(**params))
    ok()
