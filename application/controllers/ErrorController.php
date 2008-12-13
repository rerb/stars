<?php

class ErrorController extends STARS_ActionController
{
    public function errorAction()
    {
        $this->view->errors = $this->_getParam('error_handler');
        $this->view->title = 'Error';
        $errorTypes = array(
            Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_CONTROLLER, 
            Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_ACTION,
        );
        if(in_array($this->view->errors->type, $errorTypes))
        {
            $this->getResponse()->setHttpResponseCode(404);
        }
        // If this is a STARS_exception, then we'll assume it has a user friendly message and has already been logged.
        if (is_a($this->view->errors->exception, STARS_Exception)) {
            $this->view->userMessage = $this->view->errors->exception->getMessage();
        }
        else {
            watchdog('exception','Uncaught exception: '.$this->view->errors->exception->getMessage(),WATCHDOG_ERROR);
        } 
    }
    
    public function offlineAction()
    {
        $this->view->title = 'Site Offline';
        $this->getResponse()->setHttpResponseCode(503);
    }
}
