<?php

class TrackerController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $this->view->title = 'My Tracker';
        
        $normList = new STARS_NormalizationList();
        $this->view->normInfo = $normList->getInfo();
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
       throw new STARS_ErrorTicket('Could not locate the requested file.',
                                  new STARS_Exception('Failed to download form from :'.$this->view->filepath),
                                  true);
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
        // Note: this code is duplicated in InstitutionalController report
        $sections = array (
                       "ER" => 1,
                       "OP" => 2,
                       "AF" => 3,
                       "IN" => 5,
                    );
        foreach ($sections as $name => $id) {
          if ($id) {
            $section = new STARS_Section($id);
            $this->view->section[$name]->status = $section->getStatus();
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
        $file = array();
        $file['fileAvailable'] = false;
        $file['filename'] = array();
        $file['linkPath'] = '/tracker/downloadzip/zip/';

        $sectionFilenames = $this->_getZipFilenames($section);
        foreach($sectionFilenames as $filename) {
          $filepath = STARS_File::getFullFilesPath($filename, 'CREDIT_FORM');
          if (file_exists($filepath)) {
            $file['fileAvailable'] = true;
            $file['filename'][] = $filename;
          }
        }
        return $file;
    }
    
    /**
     * Helper - build the section's  zipped forms file name.
     * @param array section definition
     * @return array of filename for the ZIP files of forms for this section.
     * @todo this should be moved to a more generic module.
     */
    private function _getZipFilenames($sectionName)
    {
      $sectionLabel = str_replace(' ', '_', $sectionName);
      $filenames = array();
      $filenames[] = 'STARS-' . $sectionLabel . '-Phase1-Forms.zip';
      $filenames[] = 'STARS-' . $sectionLabel . '-Phase2-Forms.zip';
      $filenames[] = 'STARS-' . $sectionLabel . '-TierTwo-Forms.zip';
      return $filenames;
    }
}
