<?php

class SectionController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $section = new STARS_Section($this->_getParam('section'));
        
        $this->view->credits = $section->getCredits();
        
        $this->view->title = $section->getTitle();
    }
}
