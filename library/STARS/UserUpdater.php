<?php

class STARS_UserUpdater extends STARS_Abstract_UserWriter
{
    const NO_UPDATE_ERROR = -2;
    const NO_ID_ERROR = -3;
    
    public function __construct(array $info)
    {
        parent::__construct($info);
        
        if(!empty($info['password']))
        {
            $this->_makePasshash($info['password']);
        }
    }
    
    public function write()
    {
        if(empty($this->_persons['personid']))
        {
            return self::NO_ID_ERROR;
        }
        
        if(count($binds = $this->_binds()) == 1)
        {
            return self::NO_UPDATE_ERROR;
        }
        
        try
        {
            $affected = Zend_Registry::get('db')->update
            (
                new Zend_Db_Expr('persons AS p INNER JOIN datasecurity AS d ON d.personid = p.personid LEFT JOIN relpersons2orgs AS r ON r.personid = p.personid'),
                $binds,
                'p.personid = '.intval($this->_persons['personid'])
            );
            
            return ($affected !== 0) ? self::SUCCESS : self::NO_UPDATE_ERROR;
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
    }
    
    private function _binds()
    {
        $binds = array();
        
        foreach(array('persons', 'datasecurity', 'relpersons2orgs') as $table)
        {
            $arrayname = '_'.$table;
            
            foreach($this->$arrayname as $col => $value)
            {
                $binds[$table[0].'.'.$col] = $value;
            }
        }
        
        return $binds;
    }
}
