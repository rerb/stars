<?php
/**
 * Represents an error condition that the user should be alerted to.
 * Always use a STARS_ErrorTicket to record user-friendly error messages.
 * A STARS_ErrorTicket has-a Exception, which contains details about the actual error condition being raised.
 *
 */
class STARS_ErrorTicket extends STARS_Exception
{
    public $exception;     // an exception with details about this error ticket
    public $severity;      // severity of this error
    public $addContactMsg; // flag to indicate addition of contact msg. to user message.
    /**
     * Build a new ErrorTicket with a user-friendly message and a detailed exception object
     *
     * @param string $message  a user-friendly message, providing helpful information to the user
     * @param Exception $e  a detailed exception object, providing information to write to log.
     * @param boolean $addContactMsg  true if "Please contact AASHE..." should be added to the user message.
     * @param int  $severity  severity of this error (Notice, Warning, Error)
     */
    public function __construct($message = null, $e = null, $addContactMsg=false, $severity=WATCHDOG_ERROR)
    {
        parent::__construct($message);
        $this->exception = $e;
        $this->severity = $severity;
        $this->addContactMsg = $addContactMsg;
    }
}
