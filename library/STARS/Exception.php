<?php
/**
 * Represents an error condition raised by and trapped within the STARS code.
 * A STARS_Exception should NEVER be used to report a user-generated error.
 * A STARS_Exception should contain a detailed system message, suitable for debugging the issue raised.
 * A STARS_ErrorTicket should be used for exceptions that contain user-friendly messages.
 *
 */
class STARS_Exception extends Exception
{

}
