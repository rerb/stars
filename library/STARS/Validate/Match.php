<?php

class STARS_Validate_Match extends Zend_Validate_Abstract
{
    const NOT_MATCH = 'notMatch';
    
    private $_field;
    protected $_messageTemplates = array
    (
        self::NOT_MATCH => 'Fields do not match.'
    );

    public function __construct($field = null)
    {
        $this->setField($field);
    }
    
    public function getField()
    {
        return $this->_field;
    }

    public function setField($field)
    {
        $this->_field = $field;
        return $this;
    }

    public function isValid($value, $context = null)
    {
        $value = (string) $value;
        $this->_setValue($value);

        if(is_array($context))
        {
            if($value == issetor($context[$this->_field]))
            {
                return true;
            }
        }
        
        elseif(is_string($context))
        {
            if($value == $context)
            {
                return true;
            }
        }

        $this->_error(self::NOT_MATCH);
        
        return false;
    }
}
