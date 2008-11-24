<?php

// Misleading filename, I admit.

define('STARS_STATUS_INCOMPLETE', 0);
define('STARS_STATUS_NA', 1);
define('STARS_STATUS_COMPLETE', 2);

// Here are the functions.

function emptyor(&$var, $default = '')
{
	return !empty($var) ? $var : $default;
}

function issetor(&$var, $default = '')
{
	return isset($var) ? $var : $default;
}

/**
 * Search an array for any occurrence of the needle (case insensitive, partial strings)
 *
 * @param string $needle
 * @param array $haystack
 * @return bool  true if any element of the array has the needle as a sub-string
 */
function striarray($needle, $haystack)
{
    foreach ($haystack as $element) {
        if (stripos($element, $needle) !== false)
          return true;
    }
    return false;
}