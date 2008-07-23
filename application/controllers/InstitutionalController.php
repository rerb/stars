<?php

class InstitutionalController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $this->view->title = 'Edit Institutional Information';
        $form = new STARS_Form(new Zend_Config_Ini('../config/createinstitution.ini', 'config'));

        $this->view->attempted = false;

        $carnegielist = new STARS_CarnegieList;

        $form->getElement('dicarnegieclass')->setMultiOptions($carnegielist->getAsMultiOptions());

        if($this->view->submitted = $this->getRequest()->isPost() and $form->isValid($_POST))
        {
            $this->view->attempted = true;
            $this->view->code = $this->_updateInstitution($form->getValues());
        }
        
        if($this->view->submitted === false)
        {
            $institution = new STARS_Institution(STARS_Person::getInstance()->get('orgid'));
            $data = $institution->getData();

            if($data != STARS_Institution::NOT_EXISTS_ERROR)
            {
                $data = array_merge($data, $institution->getContactData());
                $form->setDefaults($data);
            }
        }
        
        $this->view->form = $form->render(new Zend_View);
    }

    private function _updateInstitution($values)
    {
        $writer = new STARS_InstitutionWriter($values);
        
        return $writer->write();
    }
}
