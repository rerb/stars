from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.decorators import runs_once
from fabric.utils import abort
from fabric.contrib.files import exists

from datetime import datetime

env.project_name = 'stars'
env.repo = "http://code.aashedev.org/svn/stars/"
env.svn_user = "releaser"
env.svn_pass = "r3l3asm3!"

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
    part = prompt("Revision, Branch or Tag ([r]/b/t): ")
    
    if part == 'r' or part == "":
        rev = prompt("Revision # (blank for latest): ")
    
        if not rev:
            rev = get_latest_revision_number()
    
        env.project_path = "%sr%s" % (env.path, rev)
        checkout_attrs = "-r %s" % rev
        checkout_path = "%strunk" % env.repo
    
    elif part == 'b':
        
        branch_name = prompt("Branch Name: ")
        env.project_path = "%sbranch_%s" % (env.path, branch_name)
        checkout_attrs = ""
        checkout_path = "%sbranches/%s" % (env.repo, branch_name)
        
        
    elif part == 't':
        
        tag_name = prompt("Tag Name: ")
        env.project_path = "%stag_%s" % (env.path, tag_name)
        checkout_attrs = ""
        checkout_path = "%stags/%s" % (env.repo, tag_name)
    else:
        print "Invalid option."
        abort(0)
    
    env.checkout_cmd = 'svn --force --no-auth-cache --non-interactive --username %s --password %s %s export %s %s' % (env.svn_user, env.svn_pass, checkout_attrs, checkout_path, env.project_path)
    
    # @Todo: I could copy over the live DB to work with...
    
def prepare_production():
    """
        Prepares a release for the production server
        Adds a tag to the repository if necessary
        sets env.project_path and env.checkout_cmd
    """
    # Get the tag from the user
    tag_name = None
    tag_name = prompt("Tag Name: ")
    while not tag_name:
        print "Please enter a new tag or existing tag (or 'q' to quit)."
        tag_name = prompt("Tag Name: ")
    if tag_name == 'q':
        abort('User terminated session.')
        
    # Create a new tag from the current trunk if "tag" doesn't exist yet
    # this assumes some control over trunk... If you are worried, create the
    # tag first yourself
    tag_path = "%stags/%s" % (env.repo, tag_name)
    if not tag_exists(tag_path):
        msg = prompt("Tag Message (no quotes, sorry): ")
        local("svn --username %s --password %s --non-interactive copy %strunk %s -m '%s'" % (env.svn_user, env.svn_pass, env.repo, tag_path, msg))
        
    env.project_path = "%stag_%s" % (env.path, tag_name)
    env.checkout_cmd = 'svn  --force --no-auth-cache --non-interactive --username %s --password %s export %s %s' % (env.svn_user, env.svn_pass, tag_path, env.project_path)

def deploy():
    """
        Deploy code to server, buildout environment and launch
    """
    env.prep()
    
    require('hosts', provided_by = [dev,production])
    
    if exists(env.project_path):
        overwrite = None
        while overwrite not in ['y', 'n', 'q']:
            overwrite = prompt("The code has already been exported from subversion. Overwite? (y/n/q):")
            if overwrite == 'y':
                sudo(env.checkout_cmd)
            elif overwrite == 'q':
                abort('User terminated session.')
            elif overwrite == 'n':
                pass
    else:
        sudo(env.checkout_cmd)
        
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

def get_latest_revision_number():
    """
        Gets the latest revision # for trunk
        Thanks, http://spindrop.us/2009/03/02/a-stitch-in-fabric-saves-time/
    """
    
    import subprocess as sub
    
    args = ['svn', '--username', env.svn_user, '--password', env.svn_pass, '--non-interactive', 'info', "%strunk" % env.repo]
    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
    output, errors = p.communicate()
    if errors:
        abort(errors)
    return output.partition('Revision: ')[2].partition('\n')[0]
    
def tag_exists(tag_path):
    """
        Checks to see if a tag exists in the repository
    """
    
    import subprocess as sub
    
    args = ['svn', '--username', env.svn_user, '--password', env.svn_pass, '--non-interactive', 'info', tag_path]
    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
    output, errors = p.communicate()
    
    if not errors:
        return True
    return False
    
def rollback():
    """
        @todo...
    """
