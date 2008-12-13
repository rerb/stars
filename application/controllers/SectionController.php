<?php

class SectionController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('section'));
        
        $this->view->title = $section->getTitle();

        // @to-do: consider re-factoring a CreditList Domain Object?
        $credits = $section->getCredits();
        
        // Load model for each credit 'object' (which is really just a record here).
        reset($credits);
        while (list($i, $credit) = each($credits)) {
          // Blank PDF Form download for this credit
          $credits[$i]['form'] = STARS_CreditPdfFile::getFormInfo($credit);
          
          // Existing submission for this credit
          $credits[$i]['submission'] = STARS_CreditPdfFile::getSubmissionInfo($credit);
          
          // Submit or Edit submission for this credit
          $credits[$i]['submit'] = STARS_CreditPdfFile::getSubmitInfo($credit);
        }
        $this->view->credits = $credits;
        $this->view->breadcrumb()->setSection($section->getSectionInfo());
    }

  /**
   * /section/validateForms
   * Admin. function to validate the forms directory
   *  Checks consistency between forms and DB
   *  Checks for valid meta-data in each form
   * @todo Move action to generic FileController
   */
  public function validateformsAction()
  {
    $this->_protect(2);
    
    $msgs = array();
    $files = array();
    // First check all files exist & are valid for each credit.
    // @to do: Here I need that CreditList DO again - I need all credits!
    $credits = STARS_Credit::getAllCredits();
    foreach($credits as $credit) {
      $filename = $credit->formFilename();
      if ( $msg = $this->_isNotValid($filename) ) {
        $msgs[$filename] = $msg;
      }
      $files[] = $filename;
    }
    
    // Check that every file has a corresponding Credit
    $dirName = STARS_File::getFullFilesPath('', 'CREDIT_FORM');
    $dir = opendir($dirName);
    $numForms = 0;
    while (false !== ($file = readdir($dir))) {
      $pathInfo = pathinfo($file);
      if ('pdf' == $pathInfo['extension'] ) {
        $numForms++;
        if (! in_array($file, $files) ) { 
          $msgs[$file] = "Form $file does NOT have matching credit in DB.";
        }
      }
    }
    $this->view->title = 'Validate Credit Forms';
    $this->view->formsDir = $dirName;
    $this->view->numCredits = count($files);
    $this->view->numForms = $numForms;
    $this->view->msgs = $msgs;
  }
  
  /**
   * Helper - validate a single form
   * @return false if form is valid, error message if it is 
   */
  private function _isNotValid($filename)
  {
    $metaTag = basename($filename, '.pdf');
    $filepath = STARS_File::getFullFilesPath($filename, 'CREDIT_FORM');
    if ( file_exists($filepath) ) {
      if (STARS_File::containsTag($filepath, $metaTag)) {  // file IS valid
        return false;
      }
      else {
        return "Form $filename does NOT contain meta-data tag: $metaTag.";
      }
    }
    else {
      return "Missing Form: $filename (credit in database)";
    }
  }
}
