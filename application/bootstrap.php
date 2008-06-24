<?php

error_reporting(E_ALL);

// INCLUDES

set_include_path('../library' . PATH_SEPARATOR 
               . '../application' . PATH_SEPARATOR 
               . get_include_path());

require_once('Zend/Loader.php');

Zend_Loader::registerAutoload();

require_once('../application/functions.php');

// CONFIG

$config = new Zend_Config_Ini('../config/main.ini', 'config');

// ROUTES

$router = Zend_Controller_Front::getInstance()->getRouter();
$router->addConfig($config->routes);

// DATABASE

$db = Zend_Db::factory($config->database);
$db->setFetchMode(Zend_Db::FETCH_ASSOC);
$db->getConnection();

// REGISTRATION

Zend_Registry::set('config', $config);
Zend_Registry::set('db', $db);

//
// Delete this if no problems arise. STARS_Person is a singleton and does not belong here.
// Zend_Registry::set('person', new STARS_Person(Zend_Auth::getInstance()->getIdentity()));
//

// FRONT CONTROLLER

$front = Zend_Controller_Front::getInstance();
$front->run('../application/controllers');
