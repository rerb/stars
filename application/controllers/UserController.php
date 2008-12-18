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
    
    /**
     * Admin function to delete an Org-Role relation for a user (STARS_Person)
     * @param int OrgPersonRoleId passed as url param
     */
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

    /**
     * Admin user selects a default org for a user.
     * @param int personorgid passed in URL - person-org-role relation to select as default.
     */
    public function defaultorgAction()
    {
        $this->_protect(2);
        $personOrgId = $this->_getParam('number');

        $personOrgRole = new STARS_PersonOrgRole($personOrgId, true);
        $success = $personOrgRole->setAsDefault();
        
        $this->_issueOrgChangeMsg($success);
        $this->_redirectBack();
    }
    
    /**
     * User selects a new organization to edit - update the user's identity.
     */
    public function selectorgAction()
    {
        $this->_protect(1);
        
        if($this->_selectorgForm->isValid($_POST)) {
            $values = $this->_selectorgForm->getValues();
            $personOrgId = $values['person2orgid'];
            $personOrgRole = new STARS_PersonOrgRole($personOrgId, true);

            // @todo this is an ACL issue - quite a tough one to solve generically... hmmmm.
            if (($pid=$personOrgRole->get('personid')) != ($uid=STARS_User::getId())) {
                watchdog('user', "Person $uid attempted to select personOrgRole $pid.", WATCHDOG_WARNING);
                $this->_redirect('/user/invalid/');
            }
            
            $success = STARS_User::selectOrg($personOrgRole);
        }
        
        $this->_issueOrgChangeMsg($success, $personOrgId);
        $this->_redirectBack();
    }

    /**
     * Helper: issue a message based on success of attempt to switch orgs.
     * @param bool $success 
     * @param int $personOrgId - the id for new person-org-role relation selected, or null to not report
     */
    private function _issueOrgChangeMsg($success, $personOrgId=null)
    {
        if ($success) {
            $message = 'Default Organization Successfully Changed.' .
                        (($personOrgId==null) ? '' : ('<br> Editing: '.$this->orglist[$personOrgId]));
            $this->_flashMessage($message);
        }
        else {
            $this->_flashMessage("Organization was NOT updated - please report error to AASHE.");
        }
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
