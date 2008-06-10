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
        
        $this->view->attempted = false;
        $this->view->submitted = $this->getRequest()->isPost();
                
        if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_insertOrganization($form->getValues());
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Enroll Organization';
    }
    
    public function indexAction()
    {
        //
        // $this->_protect(0);
        // Should we protect this page at all?
        //
        
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
