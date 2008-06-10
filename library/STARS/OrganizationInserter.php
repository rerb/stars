<?php

class STARS_OrganizationInserter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;
    
    public function __construct(array $info)
    {
        $this->_sortInfo($info);
    }
    
    public function write()
    {
        try
        {
            Zend_Registry::get('db')->insert('organizations', $this->_organizations);
                                
            return self::SUCCESS;
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
    }
    
    private function _sortInfo(array $info)
    {
        foreach($info as $key => $value)
        {
            if(in_array($key, array('nameid', 'orgname')))//removed parentorgid
            {
                $this->_organizations[$key] = $value;
            }
        }
    }
}
