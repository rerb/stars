# STARS

### Installation

See [README_VENV](https://github.com/AASHE/stars/blob/master/README_VENV) for setting up your local working environment

### Settings

The default configuration file should work right out of the box:

stars/config/settings.py

### Personal Settings

STARS can be deployed in a variety of environments. You may want to create your own personal configuration file according to your needs. You can do this easily by copying the default config file and adding another test environment item to the dictionary in stars/settings.py. The dictionary accepts regular expressions, for example:

```python
configs = {
    '/Users/jamstooks/.\*': 'ben',
}
```

Please read [README_VENV](https://github.com/AASHE/stars/blob/master/README_VENV) to set up your environment to use ENVIRONMENT VARIABLES to handle most sensitive data.

### TinyMCE (WYSIWYG Editor)

If you want to use the TinyMCE editor in your development, you will need to create a symlink in your media directory:

~/stars_media/tp/js/tiny_mce -> PATH_TO_SRC/tinyMCE/tinymce/jscripts/tiny_mce

TinyMCE is automatically pulled down by buildout.

### Quick STARS (I mean START)

...from the package directory

```sh
$ python manage.py syncdb # This initializes the DB
$ python manage.py runserver # Runs the server on http://localhost:8000/
```

### Deployment

See [README_SERVER](https://github.com/AASHE/stars/blob/master/README_SERVER) for more details

### File-Based Cache Invalidation

A management command has been added...

```sh
$ ./manage.py clear_cache [url]
```

Execute from the project root on the stars server. Copy/paste the COMPLETE url from your address bar for the report/credit in question (even including the http:// prefix). This is necessary for the function to properly parse the necessary institution and report data from the URL pattern.

This command will invalidate the cache for the submitted URL as well as the parent submission set report card if the URL is for a credit (same as if a data correction on a single credit is approved). Invalidating for the parent report card will NOT invalidate for any credit children.
