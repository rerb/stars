# Django project settings loader
# Note: systems don't have to use this file to get the local settings
# apache calls /config/[env].py explicitly

import os, re

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# any environment can have its own configuration file
# key the configurations off of project path (can have regular expression)
# (in this case it's path, but you could use computer name or something else)
configs = {
    '/var/django/projects/stars/production/.*': 'production',
    '/var/django/projects/stars/dev/.*': 'development',
    '/var/django/projects/stars/stage/.*': 'stage',
    '/Users/jamstooks/aashe/STARS/src/.*/stars': 'ben',
    '/Users/Joseph/Projects/AASHE/STARS/.*/stars': 'joseph',
}

# find the first key that matches the ROOT_PATH
config = 'default'
for k in configs.keys():
    m = re.match("(%s)" % k, ROOT_PATH)
    if m:
        config = configs[k]
        break

# Import the configuration settings file
config_module = __import__('config.%s' % config, globals(), locals(), 'stars')

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)
