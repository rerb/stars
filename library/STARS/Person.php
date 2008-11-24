<?php

class STARS_Person
{
    private $_exists;   // true if this person has an identity within STARS
    private $_info;     // array of info about this Person:
                        // personid    unique user id (uid)
                        // orgid       id of default (current) organization
                        // title       title at the organization
                        // department  dept. at org.
                        // name        user name
                        // mail        e-mail address
                        // roles       array of roles
    
    /**
     * Constructor - public must use the static factory method.
     * @param stdClass|null $uid  unique user id or null
     */
    protected function __construct($uid)
    {
        if($uid === null)
        {
            $this->_exists = false;
            return;
        }
        
        $this->_getPersonalData($uid);
    }
    
    /**
     * Person exists
     * This is true if the person was identified in the database (has an existence in STARS).
     * This could be false in the event that the logged in person 
     * has been deleted, which is possible since Zend_Auth stores its data once.
     * @return bool
     */
    public function exists()
    {
        return (bool) $this->_exists;
    }
    
    /**
     * Factory : creates a person based on a personid
     * @return STARS_Person  test exists() to determine if Person was found
     */
    public static function factory($personid)
    {
        $person = new self($personid);
        // Try the remote call even if person doesn't exsist in DB yet - may be new user.
        if ($personid !== null) {
            try {
              $remote = STARS_User::getXmlRpcClient();
              $result = $remote->getUser($personid);
              $person->_unpackIdentity($result);
            }
            // Hmmmmm - what to do if user exists but we can't get their record from remote server? 
            catch (Zend_XmlRpc_Exception $e) {   
                ;  // @todo  log an error?
            }
        }
        return $person;
    }
    
    /**
      *  Helper: unpack the identity sent from remote server into this Person
      * @param $identity array of attributes returned from remote server
      */
    protected function _unpackIdentity($identity)
    {
        $keys = array('name', 'mail', 'roles');
        foreach ($keys as $key) {
            if (isset($identity[$key])) {
                $this->_info[$key] = $identity[$key];
            }
        }
        $this->_info['starsRole'] = striArray('stars', $this->_info['roles']);
    }
    
    
    /**
     * Get Info from _info
     * @param string $key Key (usually a MySQL column name)
     * @return mixed or null if $key does not exist
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
     * Check access rights for a user
     * @param integer minLevel - access level to check
     * @return true if user has access minLevel or higher, false otherwise
     */
    public function hasAccessLevel($minLevel)
    {
        if ($this->exists()) {  // authenticated user          
          return $this->_hasRole($minLevel);
        }
        else {  // un-authenticated user...
          return ($minLevel == 0);  // everyone has access level 0
        }
    }
    
    /**
     * Get the list of organizations this person is associated with
     * @return array of organizations and the title, dept., and role at each org.  May be empty.
     */
    public function getOrgs() 
    {
        // @todo move this to a PersonOrgsList class
        if ($this->exists()) {
            $query = new STARS_Abstract_SelectList();  // this is not really right - it's called abstract, but isn't really?
            $query->from(array('r' => 'relpersons2orgs'));
            $query->joinLeft(array('o'=>'organizations'), 'o.orgid = r.orgid', array());
            $query->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'));
            $query->joinLeft('roles', 'roles.roleid = r.roleid', array('role'));
            $query->where('r.personid = '.$this->get('personid'));
            $query->order('isdefault DESC');    
            $query->order('orgname ASC'); 

            return $query->getList();
        }
        else {
            return array();
        }
    }
    
    /**
     * Helper: Check access rights for current user
     *   This is a bit of a hack until we implement proper ACL
     * @param integer minLevel - access level to check
     * @return true if user has access minLevel or higher, false otherwise
     */
    private function _hasRole($minLevel)
    {   
    	if ($minLevel == 0) {
        	return true;  // everyone has 'anonymous' role
        }
        else if ($minLevel == 1) {   // 'authenticated' role
        	return in_array('stars user', $this->_info['roles']) ||
        	       in_array('stars admin', $this->_info['roles']);
        }
        else {  //  'admin' role
        	return in_array('stars admin', $this->_info['roles']);
        }
    }
    
    /**
     * Gets personal data from DB
     * @param $uid  unique id for user to load data for
     * TO DO : User should have a list of organizations plus a default organization - add org-specfic roles
     */
    private function _getPersonalData($uid)
    {
        $row = Zend_Registry::get('db')->fetchRow
        (
            'SELECT r.*, a.fullname AS orgname FROM relpersons2orgs AS r
            LEFT JOIN organizations AS o 
            ON (r.orgid = o.orgid)
            LEFT JOIN aashedata01.institutionnames AS a
            ON (o.nameid = a.id)
            WHERE (r.personid = ?)',
            issetor($uid, 0)
/*            'SELECT d.*, r.*, p.*, a.fullname AS orgname FROM persons AS p
            LEFT JOIN datasecurity AS d
            ON (d.personid = p.personid)
            LEFT JOIN relpersons2orgs AS r 
            ON (r.personid = p.personid)
            LEFT JOIN organizations AS o 
            ON (r.orgid = o.orgid)
            LEFT JOIN aashedata01.institutionnames AS a
            ON (o.nameid = a.id)
            WHERE (p.personid = ?)',
            issetor($this->_info['personid'], 0)
*/
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
