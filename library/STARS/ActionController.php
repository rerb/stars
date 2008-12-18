<?php

class STARS_ActionController extends Zend_Controller_Action
{
    protected $_flashMessenger = null;
    private $_sessions = array();
    // @todo add protected variables:  forms and orglist
    
    public function __construct(Zend_Controller_Request_Abstract $request, Zend_Controller_Response_Abstract $response, array $invokeArgs = array())
    {
        parent::__construct($request, $response, $invokeArgs);

        $this->view->title = $this->view->breadcrumb()->getTitle();  // default title
        $this->_headerForms();
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
     * Post-dispatch hook (called by Zend after the action executes successfully, but before rendering view)
     *   - Grab any messages that need to be flashed on the view
     */
    public function postDispatch()
    {
        $messenger = $this->_getFlashMessenger();
        if ($messenger->hasMessages()) {
            $this->view->flashMessages = implode("<br />", $messenger->getMessages());
        }
    }
    
    /**
     * Support of flashMessenger use in Controllers.
     * @param string $message message to post to flash Messenger
     */
    protected function _flashMessage($message = null)
    {
        if ($message) {
            $this->_getFlashMessenger()->addMessage($message);
        }
    }
    
    /**
     * Helper - lazy init used to grab the flash messenger
     * @return  flashMessenger object
     */
    private function _getFlashMessenger()
    {
        if (!$this->_flashMessenger) { // lazy init
            $this->_flashMessenger =
            $this->_helper->getHelper('FlashMessenger');
        }
        return $this->_flashMessenger;    
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

    // @todo - define new Form class for the select org form - needs to be very compact.
    private function _headerForms()
    {
        if (STARS_User::isLoggedIn()) {
            $orgs = new STARS_PersonOrgRoleList(STARS_User::getId());
            $this->orglist  = $orgs->getAsMultiOptions();
            if (count($this->orglist) > 1) { // only bother with the form if there is something to select
                $this->_selectorgForm = new Zend_Form(new Zend_Config_Ini('../config/selectorgform.ini', 'config'));
                $this->_selectorgForm->addElementPrefixPath('STARS', 'STARS/');
                $this->_selectorgForm->setElementDecorators(array('Element')); 
                $this->_selectorgForm->getElement('person2orgid')->setMultiOptions($this->orglist);
            
                $this->view->selectOrgForm = $this->_selectorgForm->render(new Zend_View()); 
            }
        }
        $this->_loginForm = new STARS_Form(new Zend_Config_Ini('../config/loginform.ini', 'config'));

        $this->view->loginForm = $this->_loginForm->render(new Zend_View()); 
    }

    // TO DO: these methods should use the Singleton defined by Person class
    protected function _protect($minlevel)
    {
        if(! STARS_User::hasAccess($minlevel) )
        {
            $this->_redirect('/user/invalid/');
        }
    }

    protected function _protectExceptOrg($orgid)
    {
        if( (!STARS_User::isLoggedIn() or $orgid != STARS_User::getOrgid()) and STARS_User::hasAccess(2))
        {
            $this->_redirect('/user/invalid/');
        }
    }
    
    /**
     * Following an action that has no view script, this method can be used to 
     * re-direct back to the referer page, or to $default if no referer exists.
     * Use _flashMesssage to post a message to the user about success of this action before calling.
     * This method does not return!
     * @param string $default  a valid path in STARS to which user should be redirected if back is not an option.
     */
    protected function _redirectBack($default='/tracker/')
    {
        if (isset($_SERVER['HTTP_REFERER'])) {
            $target = $_SERVER['HTTP_REFERER'];
        }
        else {
            $target = $default;
        }
        $this->_redirect($target);
    }
}
