.. _example-code:

API Code Samples
================

The following are example code snippets for several programming
languages. Each demonstrates basical, low-level access to the STARS
REST API.

Python
------

.. code-block:: python

    import json
    import urllib2
    
    uri = 'stars.aashe.org'
    endpoint = 'CHANGEME'
    username = 'CHANGEME'
    key = 'CHANGME'
    
    target = "http://%s/%s&username=%s&api_key=%s" % (uri, endpoint, username, key)
    
    result = json.load(urllib2.urlopen(target))
    
    print result


Ruby
----

The following Ruby snippet requires the JSON library for Ruby. This
library is available as a gem and can be installed via::

    gem install json

Example code listing follows:

.. code-block:: ruby

    require 'rubygems'
    require 'json'
    require 'net/http'

    user = 'username'
    api_key = 'examplekey'

    def get_subcategory(subcategory_id, format='json')
        base_url = 'http://stars.aashe.org/api/|version|/credits/subcategory/{subcategory_id}/?format={format}'
        url = '#{base_url}&username={user}&api_key={api_key}'
        response = Net::HTTP.get_response(URI.parse(url))
        data = response.body

        # convert response data to native data structure
        result = JSON.parse(data)

        return result
    end


PHP
---

.. code-block:: php

		<?php
		
		$user = "username";
		$api_key = "examplekey";
		
		$request = curl_init();
		curl_setopt($request, CURLOPT_URL, 'http://stars.aashe.org/api/<version>/credits/subcategory/1/?username='. $user ."&api_key=" . $api_key);
		
		$response = curl_exec($request);
		$json = json_decode($response);
		curl_close($request);
		
		print_r($json);
		
		?>