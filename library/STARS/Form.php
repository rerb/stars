<?php

class STARS_Form extends Zend_Form
{
    private $_mini = false;
    
    public function __construct($config = null)
    {
        $this->addPrefixPath('STARS', 'STARS/');
        $this->addElementPrefixPath('STARS', 'STARS/');
        
        // This may seem like weird placement, but you need to add the 
        // prefixes before the elements and the decorators after.
        // The constructor uses $config to add the elements.
        parent::__construct($config);
        
        $class = $this->getAttrib('class'); // for empty() check in arrays below
        
        $this->setDecorators(array
        (
            'FormElements',
            'Form',
            array
            (
                'HtmlTag',
                array
                (
                    'tag' => 'table',
                    'class' => emptyor($class, 'green').($this->_mini ? ' mini' : '')
                )
            )
        ));
        
        $this->setDisplayGroupDecorators(array('FormElements', 'DisplayGroup'));
        $this->setElementDecorators(array('Element'));
    }
    
    /**
     * This function checks psuedo-required elements for completion calucations.
     * It is assumed that isValid has already been called.
     * @return bool
     */
    public function isReallyValid()
    {
        if($this->_errorsExist === true)
        {
            return false;
        }
        
        foreach($this->getElements() as $element)
        {
            if($element->getAttrib('class') == 'required')
            {
                if(trim($element->getValue()) == '')
                {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    /**
     * Set Mini
     * Mini forms basically have width: 45%
     * @param bool $flag Flag
     */
    public function setMini($flag)
    {
        $this->_mini = (bool) $flag;
    }
    
    /**
     * Essentially str_replace on every label
     * @param string $search Search
     * @param string $replace Replace
     */
    public function templateLabels($search, $replace)
    {
        foreach($this->getElements() as $element)
        {
            $element->setLabel(str_replace($search, $replace, $element->getLabel()));
        }
    }
}
