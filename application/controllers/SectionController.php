<?php

class SectionController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('section'));
        
        $this->view->title = $section->getTitle();

        $this->_flashMessage();

        $credits = $section->getCredits();
        
        // Load model for each credit 'object'.  Domain Model pattern needed here!
        reset($credits);
        while (list($i, $credit) = each($credits)) {
          // Blank PDF Form download for this credit
          $formFilename = $this->_getFormFilename($credits[$i]);
          $formFilepath = STARS_File::getFullFilesPath($formFilename, 'CREDIT_FORM');
          if (file_exists($formFilepath)) {
            $credits[$i]['formAvailable'] = true;
            $credits[$i]['formFilename'] = $formFilename;
            $credits[$i]['formLink'] = '/credit/downloadform/form/'.$formFilename;
          }
          else {
            $credits[$i]['formAvailable'] = false;
          }

          // Previous Submission for this credit
          if (! empty($credit['status'])) {
            $file = new STARS_CreditPdfFile($credit['orgcreditfileid']);
            // @todo: error handling - if file doesn't exist, DB is inconsistent with filesystem.
            $credits[$i]['filename'] = $file->getDisplayName();
            $credits[$i]['fileLink'] = '/credit/savefile/' . $credit['creditid'];
          }
          
          // Upload credit info
          $creditCode = $credit['sectionabbr'] . ' '.
                      (($credit['prerequisite'] == 1) ? 'Prereq' : 'Credit') . ' '.
                        $credit['creditnumber'];
          $credits[$i]['creditCode'] = $creditCode;
          $credits[$i]['uploadLink'] = '/credit/upload/'.$credit['creditid'];
          $uploadTitle = (empty($credit['status']) ?'Submit Data':'View / Edit your submission');
          $credits[$i]['uploadTitle'] = $uploadTitle . ' for ' . $creditCode;
        }
        $this->view->credits = $credits;
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
    // Here I need that CreditList DO again - I need all credits!
    $credits = STARS_Credit::getAllCredits();
    foreach($credits as $credit) {
      $filename = $this->_getFormFilename($credit);
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
      if ($this->_containsTag($filepath, $metaTag)) {  // file IS valid
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
  
  /**
   * Helper - check if the file contains the tag
   */
  function _containsTag($filepath, $tag)
  {
    // Method 1:  load entire file - fast, but bloated
    $pattern = "/\b$tag\b/i";
    $matches = preg_grep($pattern, file( $filepath ));
    return count($matches);
/*
    // Method 2: do linear search with short-cut exit.  More efficient.
    $fh = fopen( $filepath, 'r' ) or die ($php_errormsg);
    while (!feof($fh)) {
      $line = fgets($fh, 4096);   // hmmm - will cause problem if pattern spans line...
      if (preg_match($pattern, $line)) {
        return true;
      }
    }
    return false;  // no match found
*/
  }

    /**
     * Helper - build the credit's form file name.
     * @param array credit definition
     * @return string filename for the PDF form for this credit.
     * @todo this should be moved to a more generic module.
     */
    private function _getFormFilename($credit)
    {
      $creditNumber = $credit['creditnumber']<10?'0':'';
      $creditNumber .= $credit['creditnumber'];
      $filename = $credit['sectionabbr'] . '_' .
                (($credit['prerequisite'] == 1) ? 'Prereq' : 'Credit') . '_' .
                  $creditNumber . '.pdf';
      return $filename;
    }
    
    public function formsdownloadAction()
    {
        // Form downloads are available to the public
        // $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('number'));
        
        $credits = $section->getCredits();
        
        $this->view->title = $section->getTitle();

        // Attempt to find the downloadable form file for each credit.
        $filesDir = '/files/creditforms/';
        $filesRoot = $_SERVER['DOCUMENT_ROOT'].$filesDir;

        reset($credits);
        while (list($i, $credit) = each($credits)) {
          $filename = $credit['sectionabbr'] . ' ' .
                      (($credit['prerequisite'] == 1) ? 'Prereq' : 'Credit') . ' ' .
                      $credit['creditnumber'] . '.pdf';

          if (file_exists($filesRoot . $filename)) {
            $credits[$i]['downloadAvailable'] = true;
            $credits[$i]['filepath'] = $filesDir . $filename;
            $credits[$i]['filename'] = $filename;
          }
        }
        $this->view->credits = $credits;
    }
}
