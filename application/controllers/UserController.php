<?php

class UserController extends STARS_ActionController
{
    public function createAction()
    {
        $this->_protect(2);
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/createuserform.ini', 'config'));
        
        $orglist = new STARS_OrganizationList;
        $form->getElement('orgid')->setMultiOptions($orglist->getAsMultiOptions());
        
        $this->view->attempted = false;
        $this->view->submitted = $this->getRequest()->isPost();
                
        if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_insertUser($form->getValues());
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Create User';
    }
    
    public function indexAction()
    {
        $this->_protect(2);
        
        $userlist = new STARS_UserList();
        
        $this->view->list = $userlist->getList();
        $this->view->title = 'All Users';
    }
    
    public function invalidAction()
    {
        $this->view->title = 'Error';
    }
    
    public function editAction()
    {
        $id = $this->_getParam('number');
        
		//a specified ID means an admin is editing a user other than himself
        if(!empty($id))
        {
            $this->_protect(2);
            $person = STARS_Person::factory($id);
        }
        
		//no specified ID defaults to current user
        else
        {
            $this->_protect(1);
            $person = STARS_Person::getInstance();
        }
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/edituserform.ini', 'config'));
        $form->setAttrib('action', $_SERVER['REQUEST_URI']);
        
        $this->view->attempted = false;
        
        if($this->view->submitted = $this->getRequest()->isPost() and $form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_updateUser($form->getValues(), $person->get('personid'));
        }
        
        if($this->view->submitted === false)
        {
            $form->setDefaults($person->getAll());
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Edit User';
    }
    
    public function deleteAction()
    {
        $this->_protect(2);
        
        $this->view->code = $this->_deleteUser($this->_getParam('number'));
        $this->view->title = 'Delete User';
    }
    
    public function loginAction()
    {
        if(Zend_Auth::getInstance()->hasIdentity())
        {
            $this->view->already = true;
        }
        
        else
        {
            $this->view->already = false;
            
            if($this->_loginForm->isValid($_POST))
            {
                $values = $this->_loginForm->getValues();
                
                $auth = Zend_Auth::getInstance();
            
                $adapter = new Zend_Auth_Adapter_DbTable(Zend_Registry::get('db'));
                
                $adapter->setTableName('datasecurity')->setIdentityColumn('username') ->setCredentialColumn('passhash')->setCredentialTreatment('MD5(CONCAT(MD5(?), salt))');
                
                $adapter->setIdentity($values['loginusername']);
                $adapter->setCredential($values['loginpassword']);
               
                $this->view->attempted = true;
                $result = $auth->authenticate($adapter);
                
                if($result->isValid())
                {
                    $auth->getStorage()->write($adapter->getResultRowObject(null, array('salt', 'passhash')));
                    $this->_redirect('/dashboard/');
                }
                
                else
                {
                    $this->view->success = false;
                }
            }
            
            else
            {
                $this->view->attempted = false;
                $this->view->errors = $this->_loginForm->getMessages();
            }
        }
        
        $this->view->title = 'Login';
    }
    
    public function logoutAction()
    {
        Zend_Auth::getInstance()->clearIdentity();
    }
    
    private function _deleteUser($id)
    {
        $deleter = new STARS_UserDeleter($id);
        
        return $deleter->delete();
    }
    
    private function _insertUser($values)
    {
        $inserter = new STARS_UserInserter($values);
        
        return $inserter->write();
    }
    
    private function _updateUser($values, $id)
    {
        $values['personid'] = intval($id);
        
        $updater = new STARS_UserUpdater($values);
        
        return $updater->write();
    }
}
