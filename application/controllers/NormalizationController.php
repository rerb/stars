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

    /**
     * /normalization/export
     * Export normalization data from DB to CSV files.
     */
    public function exportAction()
    {
      // This is an admin function
      $this->_protect(2);
      set_time_limit(0); // This might take a while - don't let the script time-out...
                        // This could be bad if the script has an infinite loop!
      $form = new STARS_Form(new Zend_Config_Ini('../config/exportnorm.ini', 'config'));
       
      if ($this->_request->isPost() &&
          $form->isValid($this->_request->getPost()) )
      {
        $this->view->report = $this->_doExport();
      }
      else { // show form ONLY for GET requests
         $this->view->form = $form->render(new Zend_View);
      }
    }

    /**
     * Helper: perform Normalization Data export to CSV files
     * @return report object with $errorList and $exportList array elements
     */
    private function _doExport()
    {
      $filename = 'Normalization_export.csv';
      $report = new stdClass();
      $report->filename = $filename;
      $report->errorList = array();
    
      $records = STARS_Normalization::getAllRecords();
      if ($records == null) {
        die("Can't load Normalization Data");  // TO DO: improve error handling
      }
      $numFields = count($records[0]) - 5;  // 5 field are not client data
      $csvFile = fopen(STARS_File ::getFullFilesPath($filename,'CREDIT_EXPORT'), 'w');
      fputcsv($csvFile, array('STARS Normalization Data', ' ', 'Exported:',date("F j, Y, g:i a"))); 
      
      // TO DO: grab range of years from DB.
      $years = array('2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001');
      $yearHeadings = array('Years:');
      foreach ($years as $year) {
        $yearHeadings[] = $year;
        $pad = count($yearHeadings) + $numFields;
        $yearHeadings = array_pad($yearHeadings, $pad, '');
      }
      fputcsv($csvFile, $yearHeadings);  // TO DO: error handling
      
      // Create a list of the actual fields we want in the output file
      $keys = array_keys($records[0]);
      $nonFields = array('orgname', 'datanormid','orgid','datemodified','modifierid');
      $this->_arrayRemoveElements($keys, $nonFields);

      // Construct the headings, which are also used as data array keys, for each year.
      $headings = array();
      $blankRow = array();
      foreach ($years as $year) {
        $headings[$year] = array();
        foreach ($keys as $key) {
          $headings[$year][] = $key.'-'.$year;
        }
        $blankRow[$year] = array_fill_keys($headings[$year], '');
      }
      $headingRow = $this->_arrayMerge2D($headings, array('Institution'), true);
      
      fputcsv($csvFile, $headingRow);  // TO DO: error handling
            
      $org = $records[0]['orgname'];
      $row = $blankRow;
      $records[] = 'END-OF-FILE'; // dummy record to signal to write out last real record
      foreach ($records as $rec) {
        if ($org != $rec['orgname'] || $rec=='END-OF-FILE') {  // new org - write out the current row
          $flatRow = $this->_arrayMerge2D($row, array('Institution'=>$org), true);
          if (fputcsv($csvFile, $flatRow) === false) {
            $report->errorList[$org] = 'Could not write to CSV file';
            die("Can't write CSV line");  // TO DO: improve error handling
          }
          else {
            $report->exportList[] = $org;
          }
          if ($rec=='END-OF-FILE') 
            break;
          $row = $blankRow;
          $org = $rec['orgname'];
        }
        $year = $rec['calendaryear'];
        if ($year != NULL) {
          $this->_arrayRemoveKeys($rec, $nonFields);
          $row[$year] = array_combine($headings[$year], array_values($rec));
        }     
      } 
      fclose($csvFile);

      return $report;
    }
    
    /**
     * Helper: merge all rows from a 2D array into a simple, flat 1D array
     *         Uses php array_merge, so all its rules for merging apply here.
     * @param $array2D  array of rows to merge
     * @param @prepend  array of values to prepend to the output array
     * @param $addBlank boolean true if a blank element should be added between rows.
     * @return array 1D containing data in flat format.
     */
    private function _arrayMerge2D($array2D, $prepend, $addBlank)
    {
      $output = $prepend;
      foreach ($array2D as $row) {
        $output = array_merge($output, $row);
        if ($addBlank)
          $output[] = '';
      }
      return $output;
    }
    
    /**
     * Helper: remove a set of elements from an array
     * @param $array  the array to remove elemnts from
     * @param $values the set of values for elements to be removed
     */
    private function _arrayRemoveElements(&$array, $values)
    {
      foreach ($array as $key => $value) {
        if (in_array($value, $values)===true) {
          unset($array[$key]);
        }
      }

    }
    
    /**
     * Helper: remove a set of elements from an array
     * @param $array  the array to remove elemnts from
     * @param $keys   the set of keys for elements to be removed
     */
    private function _arrayRemoveKeys(&$array, $keys)
    {
      foreach ($array as $key => $value) {
        if (in_array($key, $keys)===true) {
          unset($array[$key]);
        }
      }

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
