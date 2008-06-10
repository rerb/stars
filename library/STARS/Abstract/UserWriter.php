<?php

abstract class STARS_Abstract_UserWriter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;
    
    protected $_datasecurity = array();
    protected $_persons = array();
    protected $_relpersons2orgs = array();
    
    abstract public function write();
    
    public function __construct(array $info)
    {
        $this->_sortInfo($info);
    }
    
    protected function _makePasshash($password)
    {
        $salt = md5(microtime().'lololololololololololololololol');
        $this->_datasecurity['salt'] = $salt;
        $this->_datasecurity['passhash'] = md5(md5($password).$salt);
    }
    
    protected function _sortInfo(array $info)
    {
        $info = STARS_Nullifier::nullify($info);
        
        foreach($info as $key => $value)
        {
            if(in_array($key, array('personid', 'firstname', 'middlename', 'lastname', 'prefix', 'suffix')))
            {
                $this->_persons[$key] = $value;
            }
            
            elseif(in_array($key, array('username', 'level')))
            {
                $this->_datasecurity[$key] = $value;
            }
            
            elseif($key == 'orgid')
            {
                $this->_relpersons2orgs[$key] = $value;
            }
        }
    }
}
