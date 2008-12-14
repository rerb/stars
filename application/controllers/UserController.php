<?php

class UserController extends STARS_ActionController
{
    // @todo: createAction is obsolete - users are only created in IRC.  Remove action & script
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

        $this->view->title = 'Administer Users';
    }
    
    public function invalidAction()
    {
        $this->view->title = 'Invalid User Privileges';
    }
    
    // @todo : update user record on submit, addorgerole, and deleteorgrole
    public function editAction()
    {
        $id = $this->_getParam('number');
        
        // @todo : editAction is now only an Admin function - users are re-directed to IRC to edit their profile - remove code
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
            $person = STARS_User::getInstance();
        }
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/edituserform.ini', 'config'));
        $form->setAttrib('action', '/user/addorgrole/'.$id); // $_SERVER['REQUEST_URI']);

        $orglist = new STARS_OrganizationList;
        $form->getElement('orgid')->setMultiOptions($orglist->getAsMultiOptions());
        
        $rolelist = new STARS_RoleList;
        $form->getElement('role')->setMultiOptions($rolelist->getAsMultiOptions());
        
/*        
        $this->view->attempted = false;
        
        if($this->view->submitted === false)
        {
            $form->setDefaults($person->getAll());
        }
*/      
        $userInfo = $person->getAll();
        $this->view->user = $userInfo;
        $this->view->userOrgs = $person->getOrgs();
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Edit User';
 /*       
    <?php if($this->code == STARS_UserUpdater::SUCCESS) { ?>
        <p>
            Profile updated.
        </p>
        <p>
            <ul>
                <li><a href="/">Go home.</a></li>
                <li><a href="/tracker/">Go to My Tracker.</a></li>
            </ul>
        </p>
    <?php } elseif($this->code == STARS_UserUpdater::NO_UPDATE_ERROR) { ?>
        <div class="errors">
            No changes have been made Either you did not enter changes, or the user does not exist.
        </div>
        <?php echo $this->form ?>
    <?php } else { ?>
        <p>
            There was an error processing your data. Please contact the <a href="mailto:webmaster@aashe.org?subject=STARS Tracking Tool">IT Team</a> with a detailed description of the problem you encountered.. Please contact the webmaster if you continue to have problems.
        </p>
    <?php } ?>     
*/   
    }
    
    public function addorgroleAction()
    {
        $this->_protect(2);
        $id = $this->_getParam('number');        
        $form = new STARS_Form(new Zend_Config_Ini('../config/edituserform.ini', 'config'));
        
        if($this->getRequest()->isPost() and $form->isValid($_POST)) {
           $person = STARS_Person::factory($id);
//           $message = $this->_addOrgRole($form->getValues(), $person);
$message = "Adding role " . $values['role'] . " for org ". $values['orgid'] . " to user " . $values[$id];
           $this->_flashMessage($message);
        }
        else {
            $this->_flashMessage("Invalid setting - please fill out form completely.");
        }

        $this->_redirect('/user/edit/'.$id);
    }
    
    public function deleteorgroleAction()
    {
        $this->_protect(2);
        $orgPersonRoleId = $this->_getParam('number');
//        $message = $this->_deleteOrgRole($orgPersonRoleId);
$message = "Deleting relOrg2Person record: " . $orgPersonRoleId;
        $this->_flashMessage($message);

        $this->_redirect('/user/edit/'); // @todo Need to get the personid back for this redirect... hmmmmm.
    }

    // @todo: deleteAction is obsolete - users are only deleted in IRC.  Remove action & script
    public function deleteAction()
    {
        $this->_protect(2);
        
        $this->view->code = $this->_deleteUser($this->_getParam('number'));
        $this->view->title = 'Delete User';
    }
    
    public function loginAction()
    {
        if( STARS_User::isLoggedIn() ) {  
            $this->_flashMessage("You're already logged in.");
            $this->_redirect('/tracker/');
        }
        else { // not logged in yet - attempt the login
            if($this->view->attempted = $this->_loginForm->isValid($_POST)) {
                $values = $this->_loginForm->getValues();

                $this->view->success = STARS_User::login($values['loginusername'], $values['loginpassword']);

                if ($this->view->success) {
                    watchdog('user', 'Session started for User '.$values['loginusername'], WATCHDOG_NOTICE);  // add link to user's profile?
                    $this->_redirect('/dashboard/');
                }
                else {
                    $this->view->message = STARS_User::getMessage();
                }
            }
            else {
                $this->view->errors = $this->_loginForm->getMessages();
            }
        }
        $this->view->title = 'Login';
    }

     public function logoutAction()
    {
        $name = STARS_User::getName();
        if (STARS_User::logout()) {
            watchdog('user', 'Session ended for User '.$name, WATCHDOG_NOTICE);  // add link to user's profile?
        }
        else if ( STARS_User::isLoggedIn() ) {
            watchdog('user', 'Attempt to logut User '.$name. ' failed', WATCHDOG_NOTICE);  // add link to user's profile?
        }
        // we don't log attempts to logout by anonymous users - who cares.
        
        $this->view->title = 'Logout';
    }
    
    // @todo delete and insert user are obsolete - remove helpers
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
    
    private function _updateUser($values, $person)
    {
        $values['personid'] = intval($person->get('personid'));
        
        $updater = new STARS_UserUpdater($values);
        
        return $updater->write();
    }
}
