<?php

class TrackerController extends STARS_ActionController
{
    public function indexAction()
    {
        $this->_protect(1);
        
        $this->view->title = 'My Tracker';
    }
}
