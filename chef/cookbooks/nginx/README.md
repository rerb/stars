Description
===========

Installs and configures nginx on the server with the sites in the `sites` node property.

Requirements
============

Platform
--------

* Ubuntu Lucid - I haven't tested on anything else

Attributes
==========

* `sites` - The list of sites to support
  * `name` - The name of the site - assumes files/default/nginx/{name} exists
  * `ssl_root` - The path to the certificate directory (will be created if necessary)
  * `ssl_cert` - The name of the cert file
  * `ssl_key` - The name of the key file