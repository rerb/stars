<?php

class ErrorController extends STARS_ActionController
{
    public function errorAction()
    {
        $this->view->errors = $this->_getParam('error_handler');
    }
}
