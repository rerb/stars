<?php

class STARS_ActionController extends Zend_Controller_Action
{
    protected $_flashMessenger = null;
    private $_sessions = array();
    
    public function __construct(Zend_Controller_Request_Abstract $request, Zend_Controller_Response_Abstract $response, array $invokeArgs = array())
    {
        parent::__construct($request, $response, $invokeArgs);
        
        $this->view->title = $this->view->breadcrumb()->getTitle();  // default title
        $this->_loginForm();
        // If we're serving the production site, be sure we're using the production DB!
        $dbEnv = Zend_Registry::get('dbEnv');
        if ($_SERVER['SERVER_NAME']=='starstracker.aashe.org') {
          if ($dbEnv != 'production') {
            throw new STARS_Exception('Production site configured to use '.$dbEnv.' DB.');
          }
        }
        else {  // on non-prod sites, display the DB envinroment being used.
            $this->view->dbEnv = $dbEnv;
        }
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
    
    /**
     * Support for session variables stored by Controllers.
     * Each controller will be given its own namespace.
     * Store a session variable for this controller.
     * @param strin $name name of the session variable to store.
     * @param mixed $value the value to store in the session
     */
    protected function _storeToSession($name, $value)
    {
      $controllerSession = new Zend_Session_Namespace( get_class($this) );
      $controllerSession->$name = $value;
    }
    
    protected function _getFromSession($name)
    {
      $controllerSession = new Zend_Session_Namespace( get_class($this) );
      return $controllerSession->$name;
    }
    
    private function _loginForm()
    {
        $this->_loginForm = new STARS_Form(new Zend_Config_Ini('../config/loginform.ini', 'config'));
        
        $this->view->loginForm = $this->_loginForm->render(new Zend_View());
    }
    
    // TO DO: these methods should use the Singleton defined by Person class
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
