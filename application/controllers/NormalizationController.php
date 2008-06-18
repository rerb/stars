<?php

class NormalizationController extends STARS_ActionController
{
    public function init()
    {
	    $this->_flashMessenger = $this->_helper->getHelper('FlashMessenger');

 	    $this->view->messages = $this->_flashMessenger->getMessages();
 	}
    
    public function indexAction()
    {
        $this->_protect(1);
        
        $normList = new STARS_NormalizationList;
        
        $this->view->list = $normList->getList();
        
        $years = $normList->existingYears();
        
        $form = new STARS_Form(new Zend_Config_Ini('../config/createnormalization.ini', 'config'));
        
        foreach(range(date('Y'), 2000) as $year)
        {
            if(!in_array($year, $years))
            {
                $form->getElement('calendaryear')->addMultiOption($year, $this->_yearRange($year));
            }
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->hasNorms = (count($this->view->list) !== 0);
        $this->view->title = 'Annual Normalization Data';
    }
    
    public function createAction()
    {
        $form = new STARS_Form(new Zend_Config_Ini('../config/createnormalization.ini', 'config'));
        
        if($form->isValid($_POST))
        {  
            $inserter = new STARS_NormalizationInserter($form->getValues());
            $inserter->write();
        }
		
		$data = $form->getValues();
		$this->_flashMessenger->addMessage($this->_yearRange($data['calendaryear']) . ' added as a normalization year.');
        $this->_redirect('/normalization/');
    }
    
    public function deleteAction()
    {
        $this->_protect(1);
        
        $datanormid = $this->_getParam('number');
        $normalization = new STARS_Normalization($datanormid);
        
        $orgid = $normalization->get('orgid');
        
        if(empty($orgid))
        {
            $this->_redirect('/normalization/');
        }
        
        $this->_protectExceptOrg($orgid);
        
        Zend_Registry::get('db')->delete('datanorm', 'datanormid = '.intval($datanormid));
		
		$data = $normalization->getData();

		$this->_flashMessenger->addMessage($this->_yearRange($data['calendaryear']) . ' deleted as a normalization year.');
			
        $this->_redirect('/normalization/');
    }
    
    public function editAction()
    {
        $this->_protect(1);
        
        $datanormid = $this->_getParam('number');
        $normalization = new STARS_Normalization($datanormid);
        $data = $normalization->getData();
        
        if($data == STARS_Normalization::NOT_EXISTS_ERROR)
        {
            $this->view->title = 'Edit Normalization Data: Error';
            $this->view->notexists = true;
            return;
        }
        
        $this->_protectExceptOrg($data['orgid']);
        
        $this->view->notexists = false;
	
		$form = new STARS_Form(new Zend_Config_Ini('../config/editnormalization.ini', 'config'));
		
		$form->templateLabels('%year%', $range = $this->_yearRange($data['calendaryear']));
		
		$form->getElement('academicstart')->setAttrib('extra', $data['calendaryear'] - 1);
		$form->getElement('academicend')->setAttrib('extra', $data['calendaryear']);
		$form->getElement('fiscalstart')->setAttrib('extra', $data['calendaryear'] - 1);
		$form->getElement('fiscalend')->setAttrib('extra', $data['calendaryear']);
		
        $this->view->attempted = false;
        
        if($this->view->submitted = $this->getRequest()->isPost())
        {
            $this->_setHiddenDates($form, $data['calendaryear']);
            
            if($form->isValid($_POST))
            {
                $this->view->attempted = true;
                $this->view->code = $this->_updateNormalization($form);
            }
        }
        
        else
        {
            $form->setDefaults($data);
            $this->_setBrokenDates($form, $data);
        }
        
        $this->view->form = $form->render(new Zend_View);
        $this->view->title = 'Edit Normalization Data: '.$range;
    }
    
    private function _setBrokenDates(STARS_Form $form, $data)
    {
        foreach(array('fiscal', 'academic') as $type)
        {
            foreach(array('start', 'end') as $endpoint)
            {
                if(preg_match('~^[0-9]{4}-[0-9]{2}-[0-9]{2}$~', $data[$type.$endpoint]))
                {
                    list(, $month, $day) = explode('-', $data[$type.$endpoint]);
                    
                    if($day != '00')
                    {
                        $form->getElement($type.$endpoint.'month')->setValue($month);
                        $form->getElement($type.$endpoint.'day')->setValue($day);
                    }
                }
            }
        }
    }
    
    private function _setHiddenDates(STARS_Form $form, $calendaryear)
    {
        foreach(array('fiscal', 'academic') as $type)
        {
            foreach(array('start', 'end') as $endpoint)
            {
                if($_POST[$type.$endpoint.'day'] == '')
                {
                    $_POST[$type.$endpoint] = '';
                    continue;
                }
                
                $year = ($endpoint == 'end') ? $calendaryear : $calendaryear - 1;
                $month = $_POST[$type.$endpoint.'month'];
                $day = sprintf('%02d', $_POST[$type.$endpoint.'day']);
                
                $_POST[$type.$endpoint] = $year.'-'.$month.'-'.$day;
            }
        }
    }

    private function _updateNormalization($form)
    {
        $values = $form->getValues();
        
        $values['status'] = $form->isReallyValid() ? STARS_STATUS_COMPLETE : STARS_STATUS_INCOMPLETE;
        $values['datanormid'] = $this->_getParam('number');
        
        $updater = new STARS_NormalizationUpdater($values);
        
        return $updater->write();
    }
    
    private function _yearRange($endYear)
    {
        // You can't use an en-dash. It's either &amp;150; or a question mark. :(
        return ($endYear-1).'-'.$endYear;
    }
}
