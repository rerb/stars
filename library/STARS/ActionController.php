<?php

class STARS_ActionController extends Zend_Controller_Action
{
    protected $_flashMessenger = null;
    
    public function __construct(Zend_Controller_Request_Abstract $request, Zend_Controller_Response_Abstract $response, array $invokeArgs = array())
    {
        parent::__construct($request, $response, $invokeArgs);
        
        $this->_loginForm();
    }
    
    /**
     * Support of flashMessenger use in Controllers.
     * @param string $message message to post to flash Messenger, or 
     *        pass null to get existing flash message to this->view->message
     */
    protected function _flashMessage($message = null)
    {
       if (!$this->_flashMessenger) { // lazy init
          $this->_flashMessenger = 
                  $this->_helper->getHelper('FlashMessenger');
       }
       if ($message) {
         $this->_flashMessenger->addMessage($message);
       }
       else if ($this->_flashMessenger->hasMessages()) {
         $this->view->message = implode("<br />", 
                     $this->_flashMessenger->getMessages());
       }
    }
    
    private function _loginForm()
    {
        $this->_loginForm = new STARS_Form(new Zend_Config_Ini('../config/loginform.ini', 'config'));
        
        $this->view->loginForm = $this->_loginForm->render(new Zend_View());
    }
    
    protected function _protect($minlevel)
    {
        if(!Zend_Auth::getInstance()->hasIdentity() or Zend_Auth::getInstance()->getIdentity()->level < $minlevel)
        {
            $this->_redirect('/user/invalid/');
        }
    }
    
    protected function _protectExceptOrg($orgid)
    {
        if(!Zend_Auth::getInstance()->hasIdentity() or ($orgid != STARS_Person::getInstance()->get('orgid') and Zend_Auth::getInstance()->getIdentity()->level < 2))
        {
            $this->_redirect('/user/invalid/');
        }
    }
}
