from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import exists
from fabric.colors import red, green
from contextlib import contextmanager as _contextmanager


env.project_name = 'stars'
env.project_root = "/var/www/%s/" % env.project_name
env.path = "%ssrc/" % env.project_root
env.repos = "ssh://hg@bitbucket.org/aashe/stars"
env.upstart_service_name = 'stars'
env.current_symlink_name = 'current'
env.previous_symlink_name = 'previous'
env.virtualenv_name = 'env'

@_contextmanager
def virtualenv():
    '''
    Custom fabric contextmanager that lets you run fabric
    commands (via sudo(), run(), etc.) with a virtualenv
    activated. Uses the `activate` fabric env attribute
    as the virtualenv activation command.

    Usage:
    with(virtualenv()):
    run("python manage.py syncdb")
    '''
    with cd(env.path):
        with prefix(env.activate):
            yield

def dev():
    '''
    Configure the fabric environment for the dev server(s)
    '''
    env.user = 'releaser'
    env.hosts = ['stars-facelift.dev.aashe.org']
    env.path = '/var/www/django_projects/stars-facelift'
    env.django_settings = 'commons.settings.dev'
    env.activate = 'source %s/%s/bin/activate' % (env.path, env.virtualenv_name)
    env.upstart_service_name = 'stars-facelift'
    env.requirements_txt = 'requirements.txt'

def deploy():
    '''
    Generic deploy function to deploy a release to the configured
    server. Servers are configured via other functions (like dev).

    For example, to deploy to the dev server, use the fabric command:

    $ fab dev deploy
    ''' 
    env.branch_name = prompt("Revision, branch or tag name (blank for default): ")
    if not env.branch_name:
        env.branch_name = 'default'
    env.changeset_id = local('hg id -r %s -i' % env.branch_name, capture=True)
    export()
    requirements()
    if not test():
        print(red("[ ERROR: Deployment failed to pass test() on remote. Exiting. ]"))
    else:
        print(green("[ PASS: Deployment passed test() on remote. Continuing... ]"))
    config()
    restart()
    
def export():
    '''
    Export the designated revision, branch or tag and then upload
    and extract the tarfile to the server. Create a code archive
    locally instead of a server-side checkout of the repository.
    '''
    export_path = '%s_%s' % (env.branch_name,
                             env.changeset_id)
    tarfile = '%s.tar.gz' % export_path
    local('hg archive -r %(branch)s -t tgz %(tarfile)s' %
          {'branch': env.branch_name, 'tarfile': tarfile})
    put(tarfile, env.path)
    local("rm %s" % tarfile)
    with cd(env.path):
        # extract tarfile to export path
        run('tar xvzf %s' % tarfile)
        run('rm -rf %s' % tarfile)
        env.release_path = '%s/%s' % (env.path, export_path)

def requirements():
    '''
    Refresh or create the remote virtualenv site-packages using
    the project's requirements.txt file.
    '''
    with virtualenv():
        print("Updating virtualenv via requirements...")
        if not hasattr(env, 'release_path'):
            env.release_path = '%s/current' % env.path
        run('pip install -r %s/%s' % (env.release_path, env.requirements_txt))

def test(): 
    '''
    Test our installation in a few ways.
    '''
    with virtualenv():
        with cd(env.release_path):
            result = run('python manage.py validate --settings=%s' % env.django_settings)
    return result.succeeded

def update_symlinks():
    with cd(env.path):
        if exists('%s' % env.previous_symlink_name):
            previous_path = run('readlink %s' % env.previous_symlink_name)
            run('rm %s' % env.previous_symlink_name)
            run('rm -rf %s' % previous_path)
        if exists('%s' % env.current_symlink_name):
            # get the real directory pointed to by current
            current_path = run('readlink %s' % env.current_symlink_name)
            # make current the new previous
            run('ln -s %s %s' % (current_path, env.previous_symlink_name))
            run('rm %s' % env.current_symlink_name)
        # update "current" symbolic link to new code path            
        run('ln -s %s %s' % (env.release_path, env.current_symlink_name))

def config():
    '''
    Configure the exported and uploaded code archive.
    '''
    update_symlinks()
    # enter new code location, activate virtualenv and collectstatic    
    with virtualenv():
        with cd(env.release_path):
            run('python manage.py collectstatic --settings=%s --noinput' %
                env.django_settings)

def restart():
    '''
    Reboot uwsgi server.
    '''
    sudo("service %s restart" % env.uwsgi_service_name)

def syncdb():
    '''
    Run "manage.py syncdb".
    '''
    with virtualenv():
        with cd("%s/current" % env.path):
            run('python manage.py syncdb --noinput --settings=%s' %
                env.django_settings)
