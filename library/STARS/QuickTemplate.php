<?php

class STARS_QuickTemplate
{
    const HTML = 1;
    const TXT = 2;
    
    private $_template;
    
    public function __construct($template)
    {
        $this->_template = $template;
    }
    
    public function bind(array $binds = array())
    {
        if(!file_exists($this->_template))
        {
            throw new STARS_Exception('QuickTemplate does not exist.');
        }
        
        if(count($binds) == 0)
        {
            return $this->templateContents();
        }
        
        return str_replace(array_keys($binds), array_values($binds), $this->templateContents());
    }
    
    public function templateContents()
    {
        return file_get_contents($this->_template);
    }
    
    public function type()
    {
        if(preg_match('~\.html?$~i', $this->_template))
        {
            return self::HTML;
        }
        
        return self::TXT;
    }
}
