# Django project settings loader
# Note: systems don't have to use this file to get the local settings
# apache calls /config/[env].py explicitly

import os, re, sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# if there is a "local.py" file then use that
if os.path.exists(os.path.join(ROOT_PATH, "config/local.py")):
    config = "local"
else:
    # any environment can have its own configuration file
    # key the configurations off of project path (can have regular expression)
    # (in this case it's path, but you could use computer name or something else)
    configs = {
        '/Users/jamstooks/.*': 'ben',
        '/Users/jesse/src/.*': 'jesse',
        '/Users/rerb/src/.*': 'bob',
        '/Users/kuranes/.*': 'matt',
        '/app/stars': 'heroku',
    }

    # find the first key that matches the ROOT_PATH
    config = 'default'
    for k in configs.keys():
        m = re.match("(%s)" % k, ROOT_PATH)
        if m:
            config = configs[k]
            break

print >> sys.stderr, "USING %s CONFIG" % config

# Import the configuration settings file
config_module = __import__('config.%s' % config, globals(), locals(), 'stars')

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)
