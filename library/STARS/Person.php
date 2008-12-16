<?php

class STARS_Person
{
    private $_exists;   // true if this person has an identity within STARS
    private $_info;     // array of info about this Person:
                        // personid    unique user id (uid)
                        // orgid       id of default (current) organization
                        // orgname     name of the organization
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
        $this->_exists = false;
        $this->_info = array();
        if($uid === null){
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
     * @param int $personid  POID of Person to create, null to create 'anonymous' person
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
            catch (Zend_XmlRpc_Client_Exception $e) {
              throw self::_getErrorTicket($person, $personid, $e);
            }
        }
        return $person;
    }
    
    /**
     * Helper: generate an error ticket for a failed RPCXML request
     *
     * @param Exception $e  - the exception to base the error ticket on
     * @return Exception $ticket  the exception to throw
     */
    private static function _getErrorTicket($person, $personid, $e)
    {
        // Possible causes: user doesn't exist on remote server; no such user; other?
        if (stripos($e->getMessage(),'user') !== false) {   // hackish way to ID user not found
            if ($person->exists()) { // Oh-oh, DB is inconsistent - person exists in STARS, but not in IRC
                $error = new STARS_ErrorTicket("User (id = $personid) not found in AASHE IRC.",
                             new STARS_Exception("DB Inconsistency: User (id = $personid) exists in STARS, but not on remote server. [".$e->getMessage().']'),
                             true, WATCHDOG_ERROR);
            }
            else {  // no such user - invalid personid passed in
                $error = new STARS_ErrorTicket("No such User (id = $personid) ", $e, true, WATCHDOG_WARNING);
            }
        }
        else {  // Could be some other rpcxml issue?
             $error = $e;  // default case: no idea, just pass the original exception along
        }
        return $error;
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
        $this->_info['personid'] = $identity['uid'];
    }
    
    
    /**
     * Get Info from _info
     * @param string $key Key (usually a MySQL column name)
     * @return mixed or null if $key does not exist
     */
    public function get($key)
    {
        // This is just a pre-caution - since much of user's data is loaded from their remote identity
        //  it should be valid to query a user that doesn't exist in STARS yet.
        if(!isset($this->_info['personid']))
        {
            watchdog('defect', "Attempt to get($key) for anonymous person", WATCHDOG_WARNING);
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
        if ($this->exists()) {
            $orgList = new STARS_PersonOrgRoleList($this->get('personid'));

            return $orgList->getList();
        }
        else {
            return array();
        }
    }
    
    /**
     * Add the given organization-role relation for this person
     *
     * @param array $values : ('roleid' 'orgid' 'title' 'department')
     */
    public function addOrgRole($values)
    {
        $values['personid']  = ($uid = $this->get('personid'));
        $values['isdefault'] = ($newUser = !$this->exists());   // make initial org-role the default. 
        Zend_Registry::get('db')->insert('relpersons2orgs', $values);
        
        // If this is a new user - load up the info we just wrote
        if (!$this->exists()) {
            $this->_getPersonalData($uid);
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
     * @todo : User should have a list of organizations plus a default organization - add org-specfic roles
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
