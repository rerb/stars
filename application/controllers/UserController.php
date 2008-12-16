<?php
// @todo  Delete DB tables, views, and classes related to obsolete actions:
//  - views/scripts/user/create.phtml & delete.phtml
//  - library/STARS/UserDeleter.php, userInserter.php, userUpdater.php, /Abstract/userWriter
//  - library/STARS/PasswordResetter, P-R-Emailer,
//  - config/createuserform.ini, resetpasswordform.ini, forgotpasswordform.ini, 
//  - DB tables: dataaddresses, datacontractinfo, persons (**** STILL USED BY Institutional ACTIONS!!!! ***)
//  - DB tables: datasecurity, passwordresetkeys
class UserController extends STARS_ActionController
{    
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
    
    /**
     * Admin function to grant/revoke privileges to STARS_user's
     * @param integer uid  user id of the user to edit
     */
    public function editAction()
    {
        $this->_protect(2);       
        $id = $this->_getParam('number');
        if(empty($id)) {
            throw new STARS_ErrorTicket('No user id specified');
         }
        
        $person   = STARS_Person::factory($id);
        $orglist  = new STARS_OrganizationList;
        $orglist  = $orglist->getAsMultiOptions();
        $rolelist = new STARS_RoleList;
        $rolelist = $rolelist->getAsMultiOptions();    
          
        $form = new STARS_Form(new Zend_Config_Ini('../config/edituserform.ini', 'config'));
        $form->setAttrib('action', $_SERVER['REQUEST_URI']);
        $form->getElement('orgid')->setMultiOptions($orglist);
        $form->getElement('roleid')->setMultiOptions($rolelist);
        
        $this->view->success = false;
        $this->view->submitted = $this->getRequest()->isPost();           
        if ($this->view->submitted and $form->isValid($_POST)) {
            $values = $form->getValues();
            unset($values['submit']);
      	    $person->addOrgRole($values);
      		$this->view->message = "Added " . $rolelist[$values['roleid']] . " role " .
      		                       " for "  . $person->get('name') . 
      		                       " at "   . $orglist[$values['orgid']];
            $this->view->success = true;           
        }
     
        $userInfo = $person->getAll();
        $this->view->user = $userInfo;
        $this->view->userOrgs = $person->getOrgs();
        
        $this->view->form = $form->render(new Zend_View);
        if ($person->exists()) {
            $this->view->title = 'Edit User : ' . $person->get('name');
        }
        else {
            $this->view->title = 'Edit New User';
        }
    } 
    
    public function deleteorgroleAction()
    {
        $this->_protect(2);
        $orgPersonRoleId = $this->_getParam('number');
        if(empty($orgPersonRoleId)) {
            throw new STARS_ErrorTicket('No person-org-role id specified');
        }
        
        if (($personOrgRole = new STARS_PersonOrgRole($orgPersonRoleId)) == null) {
            throw new STARS_ErrorTicket('Invalid id specified',
                        new STARS_Exception("Person-org-role id $orgPersonRoleId does not exit"),
                        false, WATCHDOG_WARNING);
        }
        
        $info = $personOrgRole->getAll();
        $personOrgRole->delete();
        watchdog('user', "Role {$info['roleid']} deleted from user {$info['personid']} for org {$info['orgid']}");
        $this->_flashMessage("Role has been deleted.");

        $this->_redirect('/user/edit/'.$info['personid']);
    }

    public function selectorgAction()
    {
        $this->_protect(1);
        $orgPersonRoleId = $this->_getParam('number');

        if($this->_selectorgForm->isValid($_POST)) {
            $values = $this->_selectorgForm->getValues();
            $orgPersonRoleId = $values['person2orgid'];
            STARS_PersonOrgRole::selectDefault(STARS_User::getId(), $orgPersonRoleId);
            
            $this->_flashMessage('Organization Successfully Changed : Now Editing: '.$this->orglist[$orgPersonRoleId]);
        }
        else {
            $this->_flashMessage("Organization was NOT updated - please report error to AASHE.");
        }
        
        if (isset($_SERVER['HTTP_REFERER'])) {
            $target = $_SERVER['HTTP_REFERER'];
        }
        else {
            $target = '/tracker/';
        }
        $this->_redirect($target);
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
}
