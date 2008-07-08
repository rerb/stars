<?php

class SectionController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('section'));
        
        $this->view->credits = $section->getCredits();
        
        $this->view->title = $section->getTitle();

        $this->_flashMessage();
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
