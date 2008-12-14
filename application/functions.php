<?php

// Misleading filename, I admit.

define('STARS_STATUS_INCOMPLETE', 0);
define('STARS_STATUS_NA', 1);
define('STARS_STATUS_COMPLETE', 2);

/**
 * Indicates a notice-level watchdog event; these are normally notifications
 * of normal system events that have occurred and can usually be safely ignored.
 */
define('WATCHDOG_NOTICE', 0);

/**
 * Indicates a warning-level watchdog event; this can be triggered by an error
 * in a module that does not impact the overall functionality of the site.
 */
define('WATCHDOG_WARNING', 1);

/**
 * Indicates an error-level watchdog event; could be indicative of an attempt
 * to compromise the security of the site, or a serious system error.
 */
define('WATCHDOG_ERROR', 2);

// Here are the functions.

/**
 * Log a system message.   Shamelessly stolen from Drupal.
 *
 * @param $type  The category (usually the controller) to which this message belongs.
 * @param $message   The message to store in the log.
 * @param $severity  The severity of the message. One of the following values:
 *   - WATCHDOG_NOTICE
 *   - WATCHDOG_WARNING
 *   - WATCHDOG_ERROR
 * @param $link   A link to associate with the message (e.g., referer or user involved)
 */
function watchdog($type, $message, $severity = WATCHDOG_NOTICE, $link = NULL) 
{ 
  $log = array(
      'personid'=> STARS_User::getId(),
      'type'    => $type,
      'message' => $message,
      'severity'=> $severity,
      'link'    => $link,
      'location'=> $_SERVER['REQUEST_URI'],
      'referer' => $_SERVER['HTTP_REFERER'],
      'hostname'=> $_SERVER['REMOTE_ADDR'], 
      // 'timestamp'=> time(),    // timestamp added automatically by MySQL
  );  
  // Because the watchdog is often called when an exception has occurred, 
  // we need to be careful not to generate another exception here, so if we can't do the insert, so be it -
  // that's better than an infinite loop
  try {
      Zend_Registry::get('db')->insert('watchdog', $log);
  }
  catch (Exception $e) {
      ;  // just go quietly - there's not much we can do if the DB is down.
  }
}

function emptyor(&$var, $default = '')
{
	return !empty($var) ? $var : $default;
}

function issetor(&$var, $default = '')
{
	return isset($var) ? $var : $default;
}

/**
 * Search an array or string for any occurrence of the needle (case insensitive, partial strings)
 *
 * @param string $needle
 * @param array|string $haystack
 * @return string|bool  the first element of the array has the needle as a sub-string or false if none.
 */
function striarray($needle, $haystack)
{
    if (!is_array($haystack)) {
        $haystack = array($haystack);
    }
    foreach ($haystack as $element) {
        if (stripos($element, $needle) !== false)
            return $element;
    }
    return false;
}