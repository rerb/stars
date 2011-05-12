Description
===========

Configures paths for a webapp deployment

Assumes the following structure:

{webapp_path}/
logs/ - for application specific log files
ssl/ - to server ssl certificates

{media_symlink_root} - where other media paths are linked to

Requirements
============

Platform
--------

* Any linux

Attributes
==========

* `webapp_path` - The root path of the application, for example: /var/www/{app_name}/
* `media_symlink_root` - The location where media is stored, for example: /var/www/{app_name}/media/
* `media_links` - files that need to be linked into the media root, for example: [/var/www/{app_name}/src/static/]