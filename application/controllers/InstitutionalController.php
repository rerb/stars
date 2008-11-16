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

    /**
     * Generate a detailed report on one institution's submissions
     * @param ?number=orgid - passed in url
     */
    public function reportAction()
    {
        $this->_protect(2);
        
        $orgid = $this->_getParam('number');
        $institution = new STARS_Institution($orgid);

        $this->view->title = 'Institutional Report: ' . $institution->getName();

        // Institutional Info 
        $data = $institution->getData();
        $carnegielist = new STARS_CarnegieList;
        /*
         * Wouldn't it be neat to present this data in the editable form!
         *  Need to figure out how to get correct orgid to the index action on submit..
         *  Also, TO DO: duplicate code from indexAction...
        $form = new STARS_Form(new Zend_Config_Ini('../config/createinstitution.ini', 'config'));
        $form->getElement('dicarnegieclass')->setMultiOptions($carnegielist->getAsMultiOptions());
        if($data != STARS_Institution::NOT_EXISTS_ERROR)
        {
           $data = array_merge($data, $institution->getContactData());
           $form->setDefaults($data);
        }
        $this->view->instForm = $form->render(new Zend_View);
        */
        $contactData = $institution->getContactData();
        $data['phone'] = $contactData['contactdata'];
        $data['email'] = $contactData['contactdata2'];
        $classes = $carnegielist->getAsMultiOptions();
        $data['carnegieclass'] = $classes[$data['dicarnegieclass']];
        $groups = array(
          'Basic institutional information'=>array('carnegieclass','greenwebsite','founding'),
          'Primary contact person information'=>array('firstname','middlename','lastname','title','department','phone','email','address1','address2','address3', 'city','state','postalcode','country'),
          'Contextual information'=>array('instcontext','datemodified'),
        );
        $this->view->institution = $data;
        $this->view->groups = $groups;

        // Normalization Data
        $normList = new STARS_NormalizationList(array('orgid'=>$orgid));
        $this->view->list = $normList->getList();
        $this->view->normInfo = $normList->getInfo();
        
        // Credit submissions for each section
        $this->view->section = $this->_getSectionInfo($orgid, true);
    }
    
    private function _getSectionInfo($orgid, $creditDetails=false)
    {
        // Credit Submissions
        // TO DO:  copied from tracker controller - unify.
        $ids = array (
                       "ER" => 1,
                       "OP" => 2,
                       "AF" => 3,
                       "IN" => 5,
                     );
        $sections = array();
        foreach ($ids as $name => $id) {
          $section = new STARS_Section($id, $orgid);
          $credits = $section->getCredits();
          $sections[$name]->status = $section->getStatus();
          $sections[$name]->title = $section->getTitle();

          if ($creditDetails) {
          // @to-do: copied from sectrion controller - unify
          // Load model for each credit 'object' (which is really just a record here).
            reset($credits);
            while (list($i, $credit) = each($credits)) {
              // Existing submission for this credit
              $credits[$i]['submission'] = STARS_CreditPdfFile::getCreditFileInfo($credit);
            }
            $sections[$name]->credits = $credits;
          }
        }
        return $sections;
    }
    
    /**
     * Generate a summary report on all institutions' submissions
     */
    public function summaryAction()
    {
        $this->_protect(2);

        $this->view->institutions = array();
        $orgs = new STARS_SummaryReport;
        // Section summary - how many credits, titles, etc. for each section
        $sections = STARS_Section::sectionSummary();
        foreach ($orgs->getList() as $org) {
          $orgid = $org['orgid'];
          $inst = new stdClass;
          // Institution
          $inst->link = '/institutional/report/' . $orgid;
          $inst->name = $org['orgname'];
        
          // Normalization Data
          // NOTE: not really the right rule for complete status,
          //       but this is as close as we can get without loading each norm list.
          $inst->norm = array('isComplete'  => ($org['normComplete']>=3),
                              'yearsComplete'=> $org['normComplete'],
                              'numYears'    => $org['normAttempt']);

          // Credit submissions for each section
          $inst->section = array();
          foreach($sections as $id=>$section) {
            $abbr = $section['sectionabbr'];
            $index = $abbr . '_credits';   // HACK ALERT - to work with SummaryReport
            $inst->section[$id] = new stdClass;
            $inst->section[$id]->status = array(
                              'complete'    => ($org[$index] == $section['credits']),
                              'numComplete' => $org[$index],
                              'numCredits'  => $section['credits']);
          }
          $this->view->institutions[$orgid] = $inst;
        }
        $this->view->sections = $sections;
    }

    private function _updateInstitution($values)
    {
        $writer = new STARS_InstitutionWriter($values);
        
        return $writer->write();
    }
}
