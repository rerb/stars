<?php

class PasswordController extends STARS_ActionController
{
    public function forgotAction()
    {
        $this->view->title = 'Forgot Your Password?';
        $form = new STARS_Form(new Zend_Config_Ini('../config/forgotpasswordform.ini', 'config'));
        
        $this->view->attempted = false;
        
        if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_sendResetLink($form->getValue('username'));
        }
        
        $this->view->form = $form->render(new Zend_View);
    }
    
    public function resetAction()
    {
        $this->view->title = 'Reset Password';
        $form = new STARS_Form(new Zend_Config_Ini('../config/resetpasswordform.ini', 'config'));
        
        $this->view->attempted = false;
        $this->view->noKey = false;
        
        if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_resetPassword($form->getValues());
        }
        
        if($this->getRequest()->isPost())
        {
            $this->view->submitted = true;
        }
        
        else
        {
            $key = $this->_getParam('key');
            
            if(empty($key))
            {
                $this->view->noKey = true;
                return;
            }
            
            $form->getElement('key')->setValue($key);
            $this->view->submitted = false;
        }
        
        $this->view->form = $form->render(new Zend_View);
    }
    
    private function _resetPassword($info)
    {
        $resetter = new STARS_PasswordResetter($info);
        
        return $resetter->reset();
    }
    
    private function _sendResetLink($username)
    {
        $emailer = new STARS_PasswordResetEmailer($username);
        
        return $emailer->sendLink();
    }
}
