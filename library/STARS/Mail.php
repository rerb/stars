<?php

class STARS_Mail extends Zend_Mail
{
    public function __construct()
    {
        $this->setFrom('automation@starstracker.aashe.org', 'STARS Automation');
    }
    
    public function setBodyTemplate($template, array $binds = array())
    {        
        $methods = array
        (
            STARS_QuickTemplate::HTML => 'setBodyHtml',
            STARS_QuickTemplate::TXT => 'setBodyText'
        );

        $qt = new STARS_QuickTemplate($template);
        
        $method = $methods[$qt->type()];
        
        $this->$method($qt->bind($binds));
    }
}
