<?php

class TrackerController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $this->view->title = 'My Tracker';
        
        $this->_setCreditSectionInfo();
    }

  /**
   * /section/downloadzip/?zip=filename
   * Attempt to retrieve the given file for download.
   * @param form filename is the name of the file to server
   * @todo Move action to generic FileController
   */
  public function downloadzipAction()
  {
    //Form downloads are not available to the public
    $this->_protect(1);

    $filename = $this->_getParam('zip');
    $this->view->filepath = STARS_File::getFullFilesPath($filename, 'CREDIT_FORM');
    if (! file_exists($this->view->filepath)) 
    {
       throw new STARS_Exception('Invalid Filename');
    }
    $this->view->filename = $filename;
    $this->_helper->layout->disableLayout(); // no layout for file downloads
   // TO DO: should be just one view for file downloads that take type as param.
  }

    private function _setCreditSectionInfo()
    {
        $this->view->section = array();
        // TO DO:  this info should be fetched from the DB
        //    Get itemid, itemdisplay from dataitems 
        //         where groupname = "creditcategory"
        //    But, there is no indicator in DB about status of section - 
        //         so these needed to be set here by hand.
        $sections = array (
                       "OP" => 2,
                       "AF" => 3,
                    );
        foreach ($sections as $name => $id) {
          if ($id) {
            $section = new STARS_Section($id);
            $credits = $section->getCredits();
            $this->view->section[$name]->status = $this->_getSectionStatus($credits);
            $this->view->section[$name]->path = "/section/$id/";
            $this->view->section[$name]->title = $section->getTitle();
            $this->view->section[$name]->forms = $this->_getFormInfo($name);
          }
          else {
            $this->view->section[$name]->path = false;
            $this->view->section[$name]->title = $name;
          }
        }
    }
    
    // TO DO:  we really need a file controller ... obvious here!
    //         this is duplicate code - also occurs in CreditController
    private function _getFormInfo($section)
    {
        $sectionFilename = $this->_getZipFilename($section);
        $sectionFilepath = STARS_File::getFullFilesPath($sectionFilename, 'CREDIT_FORM');
        $file = array();
        if (file_exists($sectionFilepath)) {
          $file['fileAvailable'] = true;
          $file['filename'] = $sectionFilename;
          $file['fileLink'] = '/tracker/downloadzip/zip/'.$sectionFilename;
        }
        else {
          $file['fileAvailable'] = false;
        }
        return $file;
    }
    
    private function _getSectionStatus($credits)
    {
        $status = array();
        $status['complete'] = false;
        $numCredits = count($credits);
        $numComplete = $this->_creditsComplete($credits);
        
        if ($numComplete == 0) {
          $status['msg'] = "Incomplete";
          $status['stats'] = "($numCredits Credits to be submitted)";
        }
        else if ($numComplete == $numCredits) {
          $status['msg'] = "Complete";
          $status['stats'] = "(All $numCredits Credits have been submitted)";
          $status['complete'] = true;
        }
        else { // 0 < $numComplete < $numCredits
          $status['msg'] = "Partially Complete";
          $status['stats'] = "($numComplete of $numCredits Credits submitted)";
        }
        return $status;
    }
    
    private function _creditsComplete($credits)
    {
        $count = 0;
        // Load model for each credit 'object'.  Domain Model pattern needed here!
        foreach ($credits as $credit) {
          // Previous Submission for this credit
          if (! empty($credit['status']) ) {
             $count++;
          }
        }
        return $count;
    }
    /**
     * Helper - build the section's  zipped forms file name.
     * @param array section definition
     * @return string filename for the ZIP file of forms for this section.
     * @todo this should be moved to a more generic module.
     */
    private function _getZipFilename($sectionName)
    {
      $sectionLabel = str_replace(' ', '_', $sectionName);
      $filename = 'STARS-' . $sectionLabel . '-Phase1-Forms.zip';
      return $filename;
    }
}
