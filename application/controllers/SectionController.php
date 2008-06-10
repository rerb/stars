<?php

class SectionController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('section'));
        
        $this->view->credits = $section->getCredits();
        
        $this->view->title = $section->getTitle();
    }

    public function institutionalAction()
        {
        $this->_protect(1);
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/createinstitution.ini', 'config'));
        $this->view->attempted = false;
		
       if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_insertInstitution($form->getValues());
        }
        
        else
        {
            $this->view->submitted = $this->getRequest()->isPost();
            $this->view->errors = $form->getErrors();
            $this->view->messages = $form->getMessages();
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Institutional Information';
    }

    public function normalizationAction()
    {
        $this->_protect(1);
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/createnormalization.ini', 'config'));
        $this->view->attempted = false;
		
       if($form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_insertNormalization($form->getValues());
        }
        
        else
        {
            $this->view->submitted = $this->getRequest()->isPost();
            $this->view->errors = $form->getErrors();
            $this->view->messages = $form->getMessages();
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Annual Normalization Data';
    }

    private function _updateInfo($info)
    {
        return 1;
    }

    private function _insertInstitution($values)
    {
        $inserter = new STARS_InstitutionInserter($values);
        
        return $inserter->write();
    }
    
    private function _updateInstitution($values)
    {
        $updater = new STARS_InstitutionUpdater($values);
        
        return $updater->write();
    }

    private function _insertNormalization($values)
    {
        $inserter = new STARS_NormalizationInserter($values);
        
        return $inserter->write();
    }
    
    private function _updateNormalization($values)
    {
        $updater = new STARS_NormalizationUpdater($values);
        
        return $updater->write();
    }
}
