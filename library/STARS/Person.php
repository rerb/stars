<?php

class STARS_Person
{
    private $_exists;
    private $_info = array();
    private static $_instance = null;
    
    /**
     * Constructor
     * @param stdClass|null $identity Zend_Auth identity
     */
    public function __construct($identity)
    {
        if($identity === null)
        {
            $this->_exists = false;
            return;
        }
        
        foreach($identity as $key => $value)
        {
            $this->_info[$key] = $value;
        }
        
        $this->_getPersonalData();
    }
    
    /**
     * Person exists
     * This will only return false in the event that the logged in person 
     * has been deleted, which is possible since Zend_Auth stores its data once.
     * @return bool
     */
    public function exists()
    {
        return (bool) $this->_exists;
    }
    
    /**
     * Factory
     * This creates a person based on a personid other than that stored in Zend_Auth
     * @return STARS_Person
     */
    public static function factory($id)
    {
        $psuedoAuth = new StdClass;
        $psuedoAuth->personid = intval($id);
        return new self($psuedoAuth);
    }
    
    /**
     * Get Info from _info
     * @param string $key Key (MySQL column name)
     * @return mixed
     * @throws STARS_Exception
     */
    public function get($key)
    {
        if(!$this->exists())
        {
            throw new STARS_Exception('Person does not exist.');
            return;
        }
        
        return issetor($this->_info[$key]);
    }
    
    /**
     * Get entire _info array
     * @return array
     */
    public function getAll()
    {
        return $this->_info;
    }
    
    /**
     * Singleton
     * @return STARS_Person
     */
    public static function getInstance()
    {
        if(self::$_instance === null)
        {
            self::$_instance = new self(Zend_Auth::getInstance()->getIdentity());
        }
        
        return self::$_instance;
    }
    
    /**
     * Gets personal data from DB
     */
    private function _getPersonalData()
    {
        $row = Zend_Registry::get('db')->fetchRow
        (
            'SELECT d.*, r.*, p.* FROM persons AS p
            LEFT JOIN datasecurity AS d
            ON (d.personid = p.personid)
            LEFT JOIN relpersons2orgs AS r 
            ON (r.personid = p.personid)
            WHERE p.personid = ?',
            issetor($this->_info['personid'], 0)
        );
        
        if($row === null)
        {
            $this->_exists = false;
            return;
        }
        
        foreach($row as $key => $value)
        {
            $this->_info[$key] = $value;
        }
        
        $this->_exists = true;
    }
}
