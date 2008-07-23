<?php

class ErrorController extends STARS_ActionController
{
    public function errorAction()
    {
        $this->view->errors = $this->_getParam('error_handler');
        $this->view->title = 'Error';
        if(in_array($this->view->errors->type, array(Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_CONTROLLER, Zend_Controller_Plugin_ErrorHandler::EXCEPTION_NO_ACTION)))
        {
            $this->getResponse()->setHttpResponseCode(404);
        }
    }
}
