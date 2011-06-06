from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.decorators import runs_once
from fabric.utils import abort
from fabric.contrib.files import exists
from fabric.contrib import project, files

from datetime import datetime

from mercurial import ui, hg
from mercurial import commands

env.project_name = 'stars'
env.project_root = "/var/www/%s/" % env.project_name
env.path = "%ssrc/" % env.project_root
env.repo = "ssh://hg@bitbucket.org/ben_aashe/stars"

def vagrant():
    """
        Initializes a release to the vagrant VM host
    """
    env.hosts = ['ben-aashe-web1']
    env.user = 'vagrant'
    env.key_filename = '/Library/Ruby/Gems/1.8/gems/vagrant-0.7.3/keys/vagrant'
    env.config_file = "vagrant" 
    
def starsapp01():
    """
        Initializes a release to the production server
    """
    env.hosts = ['starsapp01']
    env.user = 'jamstooks'
    env.config_file = "starsapp01"

def setup():
    """
        Initialize the app's environment.
        Chef handles the server config.
    """
    sudo("mkdir -p %s" % env.path)
    sudo('mkdir -p %smedia/' % env.project_root)
    sudo('mkdir -p %slogs/' % env.project_root)
    sudo("ln -s %scurrent/stars/static %smedia/static" % (env.path, env.project_root))

def deploy():
    """
        Deploy code to server, buildout environment and launch
    """
    pull()
    config()
    
    with cd(env.project_path):
        buildout()
        test()
        migrate()
    
    launch()
    restart_celery()

def pull():
    """
      Pulls code from repo into new folder
    """

    branch_name = prompt("Branch or Tag Name (blank for HEAD): ")
  
    if not branch_name:
      branch_name = "default"
    env.project_path = "%s%s/" % (env.path, branch_name)
    env.hg_update_commands = [
                              "hg update %s" % branch_name,
                              "echo \"revision = '%s'\" > stars/config/hg_info.py" % branch_name,
                              ]
    env.checkout_cmd = 'hg clone --noninteractive %s %s' % (env.repo, env.project_path)

    export = None
    if exists(env.project_path):
      while export not in ['y', 'n', 'q', '']:
          export = prompt("The code has already been exported. Overwrite? ([y]/n/q):")
      
          if export == 'y' or export == '':
              with cd(env.project_path):
                  sudo('hg pull %s' % env.repo)
                  for cmd in env.hg_update_commands:
                      sudo(cmd)
          elif export == 'n':
              pass
          elif export == 'q':
              abort('User terminated session.')
    else:
      sudo(env.checkout_cmd)

      with cd(env.project_path):
          for cmd in env.hg_update_commands:
              sudo(cmd)

def config():
    "symlink the local config file"
    
    config_file_path = "%sstars/config/%s.py" % (env.project_path, env.config_file)
    config_local_path = "%sstars/config/local.py" % (env.project_path)
    
    rm_cmd = "rm %s" % config_local_path
    ln_cmd = "ln -s %s %s" % (config_file_path, config_local_path)
    
    if exists(config_local_path):
        sudo(rm_cmd)
    sudo(ln_cmd)

def buildout():
    " runs buildout "
    
    bootstrap = prompt("Run Buildout? ([y]/n):")
    
    if not bootstrap or bootstrap == 'y':
        print "Bootstrapping"
        bootstrap_cmd = "python bootstrap.py"
        sudo(bootstrap_cmd)

        print "Running Buildout"
        buildout_cmd = "bin/buildout"
        sudo(buildout_cmd)
        
@runs_once   
def test():
    "Run tests"
    
    test = prompt("Run Tests? ([y]/n):")
    
    if not test or test == 'y':
        print "Running Test Suite"
        test_cmd = "bin/django test"
        with settings(warn_only=True):
            result = sudo(test_cmd)
            if result.failed:
                abort("Test suite FAILED. Aborting.")

def migrate():
    "Run syncdb and South migrations"
    
    print "Sync DB"
    syncdb_cmd = "bin/django syncdb"
    sudo(syncdb_cmd)
    
    print "Migrate DB"
    migrate_cmd = "bin/django migrate --delete-ghost-migrations"
    sudo(migrate_cmd)
    
def launch():
    "Finalize the deployment by creating a symlink"
    with cd(env.path):
        print "Updating Symlink"
        symlink_cmd1 = "rm -rf current"
        symlink_cmd2 = "ln -s %s current" % env.project_path
        if exists("current"):
            sudo(symlink_cmd1)
        sudo(symlink_cmd2)
    
    print "Restarting Apache"
    restart_cmd = "apache2ctl graceful"
    sudo(restart_cmd)
    
def restart_celery():
    " Restart the celery upstart service "
    sudo('restart stars-celery')

def run_chef():
    """
    Run Chef-solo on the remote server
    """
    project.rsync_project(local_dir='chef', remote_dir='/tmp', delete=True)
    sudo('rsync -ar --delete /tmp/chef/ /etc/chef/')
    # sudo('chef-solo')
