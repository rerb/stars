<?php

class STARS_Abstract_SelectRow extends Zend_Db_Select
{
    const NOT_EXISTS_ERROR = -2;
    
    protected $_row = null;
    
    public function __construct()
    {
        parent::__construct(Zend_Registry::get('db'));
    }
    
    public function get($key)
    {
        $data = $this->getData();
        
        return issetor($data[$key]);
    }
    
    public function getData()
    {
        if($this->_row === null)
        {
            $this->_row = Zend_Registry::get('db')->fetchRow($this->__toString());
        }
        
        return ($this->_row === null) ? self::NOT_EXISTS_ERROR : $this->_row;
    }
}
