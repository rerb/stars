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
