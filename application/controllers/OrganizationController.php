<?php

class OrganizationController extends STARS_ActionController
{
    public function enrollAction()
    {
        $this->_protect(2);
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/createorganizationform.ini', 'config'));
        
        $orglist = new STARS_OrganizationList;
        
        $multiOptions = array_merge(array(0 => 'None'), $orglist->getAsMultiOptions());
        
       // $form->getElement('parentorgid')->setMultiOptions($multiOptions);
        
        $this->view->error = false;
        $this->view->submitted = $this->getRequest()->isPost();
                
        if($form->isValid($_POST))
        {
            if ($this->_insertOrganization($form->getValues()) == STARS_OrganizationInserter::SUCCESS) {
		        $this->_flashMessage("The organization has been created/enrolled successfully");
                $this->_redirect('/dashboard/');
            }
            else {
                // @todo log a message here to the watchdog with some context info.
                // Can probably tell quite a bit here:  duplicate orgid would be good to catch.
                $this->view->error = true;
            }
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Enroll Organization';
    }
    
    public function indexAction()
    {
        //
         $this->_protect(2);
        // Should we protect this page at all?
        // Yes - because it now lists database ID's for each organization (JF)
        
        $orgList = new STARS_OrganizationList();
        //$orgList->where('nameid <> 0');
        
        $this->view->list = $orgList->getList();
        $this->view->title = 'Enrolled Organizations';
    }
    
    private function _insertOrganization($values)
    {
        $inserter = new STARS_OrganizationInserter($values);
        
        return $inserter->write();
    }
}
