#!/usr/bin/env python

import os, sys, commands, time, re, shutil
from datetime import datetime

USAGE = """Usage: release.py [option] (path)
Example: python release.py -update ( <optional> path/to/tag )
Options:

-update (path/to/tag)

1. Check out stars as stars_[now]
2. Delete all stars_[date] directories that aren't linked from stars or stars_[now]
3. Link stars to stars_[now]
4. Restart web service

-revert

1. Find the directory currently linked from stars
2. Link stars to the directory with the previous date: stars_[previous]
3. Delete the currently linked code (you're reverting because it didn't work)
4. Restart web service (mod_python requires a restart to load new code)
"""

# The name of the project.
# Releases will be named PROJECT_MM-DD-YY_HHMMSS
# and the link will be called PROJECT
PROJECT = "stars"

# The URL of the svn repository
#REPOSITORY = "svn://aashe.org/stars/"
REPOSITORY = "file:///usr/local/repos/stars/"

# The path to the branch or release that should be
# released by default
DEFAULT_RELEASE = "branches/branch-1.0/stars"

# This is not implemented, but it could be possible to
# leave a certain # of releases in the directory
#MAX_RELEASES = 1

def date_from_stamp(stamp, prefix):
    """ returns a date when given a string version: MM-DD_YY_HHMMSS """
    m = re.match(r"^((\d{2})-(\d{2})-(\d{2})_(\d{2})(\d{2})(\d{2}))$", stamp)
    if m:
        return datetime(month=int(m.groups()[1]), day=int(m.groups()[2]), year=int(m.groups()[3]), hour=int(m.groups()[4]), minute=int(m.groups()[5]), second=int(m.groups()[6]))
    else:
        return none

def get_file_and_date(filename, prefix):
    """ returns the filename and the date of the file as a datetime in a dictionary """
    matches = re.match(r"^%s_(\d{2}-\d{2}-\d{2}_\d{6})$" % prefix, filename)
    if matches:
        date = date_from_stamp(matches.groups()[0], "%m-%d-%y_%H%M%S")
        return {'file': filename, 'date': date}
    else:
        return None
        
def compare_releases(r1, r2):
    """ Compares two releases by date. Used to sort the list of releases """
    return cmp(r1['date'], r2['date'])

path = os.path.dirname(os.path.abspath(__file__))

# find all the release files
files = os.listdir(path)
release_list = []

for f in files:
    release_dict = get_file_and_date(f, PROJECT)
    if release_dict:
        release_list.append(release_dict)

# sort the list from oldest to newest
release_list.sort(compare_releases)

# find out which release is current (linked to from PROJECT)
if os.path.exists(os.path.join(path, PROJECT)):
    print os.path.basename(os.readlink(os.path.join(path, PROJECT)))
    current = get_file_and_date(os.path.basename(os.readlink(os.path.join(path, PROJECT))), PROJECT)
    if current and current not in release_list:
        print "The current link is not in the same directory. That buggers it all up. Exiting..."
        sys.exit()
else:
    current = None

# ok now do what's asked?
if len(sys.argv) < 2 or len(sys.argv) > 3:
    print "Wrong Number of Arguments"
    print USAGE
    sys.exit()
    
if sys.argv[1] == '-update' and len(sys.argv) <= 3:
    if len(sys.argv) == 3:
        checkout_path = sys.argv[2]
    else:
        checkout_path = DEFAULT_RELEASE
        
    new_file = "%s_%s" % (PROJECT, datetime.now().strftime("%m-%d-%y_%H%M%S"))
    """
    1. Check out stars as stars_[now]
    2. Delete all stars_[date] directories that aren't linked from stars or stars_[now]
    3. Link stars to stars_[now]
    4. Restart web service
    """
    # TODO this should use some better URL path error checking
    # 1
    cmd = "svn export %s/%s %s" % (REPOSITORY, checkout_path, new_file)
    os.system(cmd)
    if not os.path.exists(os.path.join(path, new_file)):
        print "SVN Export Failed"
        sys.exit()
        # TODO: this should exit with an error and not continue if the
        # command fails for any reason.
    # 2
    for r in release_list:
        if r != current:
            shutil.rmtree(os.path.join(path, r['file']))
    # 3
    if os.path.exists(os.path.join(path, new_file)):
        # if the new file was created successfully, update the symlink
        if os.path.exists(os.path.join(path, PROJECT)):
            os.remove(os.path.join(path, PROJECT))
        os.symlink(os.path.join(path, new_file), os.path.join(path, PROJECT))
    else:
        print "CHECKOUT FAILED"
        sys.exit()
    # 4
    print "** Restarting Apache"
    cmd = "/usr/sbin/apache2ctl graceful"
    os.system(cmd)
    
elif sys.argv[1] == '-revert':
    """
    1. Find the directory currently linked from stars
    2. Link stars to the directory with the previous date: stars_[previous]
    3. Delete the currently linked code (you're reverting because it didn't work)
    4. Restart web service (mod_python requires a restart to load new code)
    """
    if release_list.index(current) > 0:
        # if there are previous releases
        previous = release_list[release_list.index(current)-1]
        print "linking %s to %s" % (PROJECT, previous['file'])
        os.remove(os.path.join(path, PROJECT))
        os.symlink(os.path.join(path, previous['file']), os.path.join(path, PROJECT))
        print "removing %s" % current['file']
        shutil.rmtree(os.path.join(path, current['file']))
        cmd = "/usr/sbin/apache2ctl graceful"
        os.system(cmd)
    else:
        print "No Previous Release"
else:
    print "Invalid Options"
    print USAGE
    sys.exit()

