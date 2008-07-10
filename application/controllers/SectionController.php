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
