<?php

class STARS_UserInserter extends STARS_Abstract_UserWriter
{
    const USERNAME_ERROR = -2;
    
    public function __construct(array $info)
    {
        parent::__construct($info);
        $this->_makePasshash(issetor($info['password']));
    }
    
    public function write()
    {
        try
        {
            $rows = Zend_Registry::get('db')->fetchOne('SELECT securityid FROM datasecurity WHERE username = ?', $this->_datasecurity['username']);
            
            if($rows !== false)
            {
                return self::USERNAME_ERROR;
            }
            
            Zend_Registry::get('db')->insert('persons', $this->_persons);
            
            $this->_relpersons2orgs['personid'] = ($this->_datasecurity['personid'] = Zend_Registry::get('db')->lastInsertId());
            
            Zend_Registry::get('db')->insert('datasecurity', $this->_datasecurity);
            Zend_Registry::get('db')->insert('relpersons2orgs', $this->_relpersons2orgs);
                    
            return self::SUCCESS;
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
    }
}
