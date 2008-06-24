<?php

class Zend_View_Helper_BaseUrl
{
    function baseUrl()
    {
        $fc = Zend_Controller_Front::getInstance();
        $request = $fc->getRequest(); /* @var $request Zend_Controller_Request_Http */
        return $request->getBaseUrl();
    }
}