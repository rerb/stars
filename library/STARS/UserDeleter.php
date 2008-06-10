<?php

class STARS_UserDeleter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;
    const NOT_EXISTS_ERROR = -2;
    const SELF_ERROR = -3;
    
    private $_id;
    
    public function __construct($id)
    {
        $this->_id = intval($id);
    }
    
    public function delete()
    {
        if($this->_id == STARS_Person::getInstance()->get('personid'))
        {
            return self::SELF_ERROR;
        }
        
        try
        {
            return (Zend_Registry::get('db')->delete('datasecurity', 'personid = '.$this->_id) == 0) ? self::NOT_EXISTS_ERROR : self::SUCCESS;
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
    }
}
