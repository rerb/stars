from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.decorators import runs_once
from fabric.utils import abort
from fabric.contrib.files import exists

from datetime import datetime

from mercurial import ui, hg
from mercurial import commands

env.project_name = 'stars'
env.hg_user = "releaser"
env.hg_pass = "r3l3asm3!"
env.repo = "https://%s:%s@code.aashedev.org/hg/stars" % (env.hg_user, env.hg_pass)

def dev():
    " Initializes a release to dev "
    
    env.hosts = ['stars.dev.aashe.org',]
    env.path = "/var/django/projects/stars/dev/"
    env.run_test = False
    env.prep = prepare_dev
    
def production():
    " Initializes a release to production "
    
    env.hosts = ['stars.aashe.org',]
    env.path = "/var/django/projects/stars/production/"
    env.run_test = True
    env.prep = prepare_production

@runs_once
def test():
    with settings(warn_only=True):
        result = local('./bin/django test', capture=False)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")    

def prepare_dev():
    """
        Prepares a release to the dev server
        sets env.project_path and env.checkout_cmd
    """
    env.extra_hg_commands = []
    
    branch_name = prompt("Branch or Tag Name (blank for HEAD): ")
        
    if not branch_name:
        branch_name = "default"
    env.project_path = "%s%s" % (env.path, branch_name)
    env.extra_hg_commands.append("hg update %s" % branch_name)
    
    env.checkout_cmd = 'hg clone --noninteractive %s %s' % (env.repo, env.project_path)
        
    # @Todo: I could copy over the live DB to work with...
    
def prepare_production():
    """
        Prepares a release for the production server
        Requires an existing tag
        sets env.project_path and env.checkout_cmd
    """
    # Get the tag from the user
    tag_name = None
    print "Please enter an existing tag (or 'q' to quit)."
    while not tag_name:
        tag_name = prompt("Tag Name: ")
    if tag_name == 'q':
        abort('User terminated session.')
    
    env.project_path = "%stag_%s" % (env.path, tag_name)
    env.extra_hg_commands = ["hg update %s" % tag_name,]
    env.checkout_cmd = 'hg clone --noninteractive %s %s' % (env.repo, env.project_path)
        
    # Create a new tag from the current trunk if "tag" doesn't exist yet
    # this assumes some control over trunk... If you are worried, create the
    # tag first yourself
#    tag_path = "%stags/%s" % (env.repo, tag_name)
#    if not tag_exists(tag_path):
#        msg = prompt("Tag Message (no quotes, sorry): ")
#        local("svn --username %s --password %s --non-interactive copy %strunk %s -m '%s'" % (env.svn_user, env.svn_pass, env.repo, tag_path, msg))
#        
#    env.project_path = "%stag_%s" % (env.path, tag_name)
#    env.checkout_cmd = 'svn  --force --no-auth-cache --non-interactive --username %s --password %s export %s %s' % (env.svn_user, env.svn_pass, tag_path, env.project_path)

def deploy():
    """
        Deploy code to server, buildout environment and launch
    """
    env.prep()
    
    require('hosts', provided_by = [dev,production])
    
    export = None
    if exists(env.project_path):
        while export not in ['y', 'n', 'q']:
            export = prompt("The code has already been exported. Overwrite? ([y]/n/q):")
            if export == 'y' or not export:
                sudo(env.checkout_cmd)
            elif export == 'q':
                abort('User terminated session.')
            elif export == 'n':
                pass
    else:
        sudo(env.checkout_cmd)
    
        with cd(env.project_path):
            for cmd in env.extra_hg_commands:
                sudo(cmd)
        
    bootstrap = None
    if export:
        bootstrap = prompt("Perform buildout, testing, and migration? ([y]/n):")
    
    if not bootstrap or bootstrap == 'y':
        with cd(env.project_path):
            print "Bootstrapping"
            bootstrap_cmd = "python bootstrap.py"
            sudo(bootstrap_cmd)
    
            print "Running Buildout"
            buildout_cmd = "bin/buildout"
            sudo(buildout_cmd)
            
            # @Todo: run tests
            print "Running Test Suite"
            test_cmd = "bin/django test"
            result = sudo(test_cmd)
            if result.failed:
                abort("Test suite FAILED. Aborting.")
            
            print "Sync DB"
            syncdb_cmd = "bin/django syncdb"
            sudo(syncdb_cmd)
            
            print "Migrate DB"
            migrate_cmd = "bin/django migrate"
            sudo(migrate_cmd)
        
    with cd(env.path):
        print "Updating Symlink"
        symlink_cmd1 = "rm current"
        symlink_cmd2 = "ln -s %s current" % env.project_path
        if exists("current"):
            sudo(symlink_cmd1)
        sudo(symlink_cmd2)
        
    print "Restarting Apache"
    restart_cmd = "apache2ctl graceful"
    sudo(restart_cmd)

    # @Todo: run cleanup
    
def tag_exists():
    """
        Checks to see if a tag exists in the repository
    """
    
    hg_ui = ui.ui()
    repo = hg.repository(ui.ui(), env.repo)
    hg_ui.pushbuffer()
    commands.tags(hg_ui, repo)
    buff = hg_ui.popbuffer()
    print buff # This fails with remote repos
    
    
#    import subprocess as sub
#    
#    args = ['svn', '--username', env.svn_user, '--password', env.svn_pass, '--non-interactive', 'info', tag_path]
#    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
#    output, errors = p.communicate()
#    
#    if not errors:
#        return True
#    return False
    
def rollback():
    """
        @todo...
    """
