<?php

class ErrorController extends STARS_ActionController
{
    public function errorAction()
    {
        $errors = $this->_getParam('error_handler');
        $this->view->addContactMsg = true;
        
        $pageNotFound = array(
            Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_CONTROLLER, 
            Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_ACTION,
        );
        if(in_array($errors->type, $pageNotFound)) {
            $this->getResponse()->setHttpResponseCode(404);
            $this->view->pageNotFound = true;
            $this->view->addContactMsg = false;
            watchdog('not found','Page Not Found: '.$errors->exception->getMessage(),WATCHDOG_WARNING);
        }
        else if (is_a($errors->exception, 'Zend_Db_Adapter_Exception')) {
            // Handle DB exceptions seperately, since they cannot be logged in the watchdog :-(
            $this->view->dbError = true;
            // Ideally, we would ....
            // if (user has admin rights)
            //    $this->view->userMessage = $errors->exception->getMessage();
        }
        else if (is_a($errorTicket=$errors->exception, 'STARS_ErrorTicket')) {
            // STARS_ErrorTicket should have a user friendly message & a more detailed exception object for log
            $this->view->userMessage = $errorTicket->getMessage();
            $this->view->addContactMsg = $errorTicket->addContactMsg;
            if (is_a($e=$errorTicket->exception, 'Exception')) {  // the ticket has an exception to log...
                watchdog(get_class($e), $e->getMessage(), $errorTicket->severity);
            }
        }
        else {  // No user message with this exception - let the view print generic message.
            watchdog(get_class($errors->exception),'Uncaught exception: '.$errors->exception->getMessage(),WATCHDOG_ERROR);
        } 
       // The exception object contains lots of info about where it was generated - could add this to watchdog in future?
    }
    
    public function offlineAction()
    {
        $this->view->title = 'Site Offline';
        $this->getResponse()->setHttpResponseCode(503);
    }
}
