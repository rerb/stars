<?php
/**
 * User is a Singleton representing THE user for this session.
 * Most functions are provided as static methods for convenience,
 *   so you don't have to get the instance - just call the static method.
 * Every user must be a STARS_Person.
 * The STARS_user is created through the authentication process - the instance is stored by
 * Zend_Auth during authentication - this class wraps up that instance.
 * Thus, this class relies on the authentication process to createUser(), then store in Zend_Auth.
 * All methods assume ACL has been applied, and user has rights to perform this operation.
 *
 */
class STARS_User extends STARS_Person
{
   // Singleton object is actually stored by Zend_Auth
   private static $_message = '';    // last message generated by operation on user
   private $_xmlrpcClient;    // client used for remote authentication.
   
   /**
     * Constructor  (should be private - Singleton - PHP grrrr.)
     * @param stdClass|null $uid  unique user id or null
     */
    protected function __construct($uid)
    {
        parent::__construct($uid);
        $this->_xmlrpcClient = new STARS_XmlRpc_Client();
    }
    
    /**
     * User is logged in?
     * This is true if authentication passed and user exists in the DB.
     * @return bool  true if user is logged in, false otherwise
     */
    public static function isLoggedIn()
    {
        $user = self::getInstance();
        return is_a($user,"STARS_User") && $user->exists();   // check class is safety - may catch odd login faults.
    }
    
    /**
     * Create a user by logging them in
     * @param string $username  
     * @param string $password
     * @return bool true if login was success, false otherwise - call getMessage() to get error message.
     */
    public static function login($username, $password)
    {
        $auth = Zend_Auth::getInstance();
        $adapter = new STARS_Auth_Adapter_XmlRpc($username, $password);
        $login = $auth->authenticate($adapter);          
        
        if($login->isValid()) {
            $user = self::_createUser( $login->getIdentity(), $adapter);
            if ($user->_hasStarsAccess()) {   // SUCCESS!
                $auth->getStorage()->write( $user );
                return true;
            }
            else {  // Login was OK, but user has no access to STARS - log them out.
                self::$_message = "You do not yet have any permissions in STARS - please contact AASHE.";
                self::logout();
                return false;
            }
        }
        else {   // Log-in failed - let the user know why...
            Zend_Auth::getInstance()->clearIdentity();         
            switch ($login->getCode()) {
                case Zend_Auth_Result::FAILURE_IDENTITY_NOT_FOUND :
                    self::$_message='The username or password you entered was incorrect. <a href="http://drupalsandbox.aashedev.org/user/password">Forgot your password?</a>';
                    break;
                default :
                    self::$_message='Server or Network error: Could not complete login - please try later.';
                    throw new STARS_ErrorTicket(self::$_message, null, true);
            }
            return false;
        }
    }
    
    /**
     * Create Identity (factory method)
     * This is intended to be called during authentication to create the user object,
     * the returned user object is to be stored in Zend_Auth.
     * @param array $identity  elements of user's identity obtained during authentication
     * @param STARS_Auth_Adapter_XmlRpc  adapter used to authenticate the user.
     * @return STARS_User
     */
    private static function _createUser($identity, $adapter)
    {
    	if (!isset($identity['uid'])) {
    		return self::factory(null);
    	}
        $user = new self($identity['uid']);
        $user->_unpackIdentity($identity);
        $user->_xmlrpcClient = $adapter->getXmlRpcClient();  // store the RPC client with user's session info
        return $user;
    }
    
    /**
     * Helper: Determine if the user has privliges to log into STARS.
     *   A user has access if they have any STARS role and exist in the STARS db
     */
    private function _hasStarsAccess()
    {
        // Don't try to get fancy here: if the person doesn't exist, get() will throw exception!
        if ($this->exists()) {
            $roles = $this->get('roles');
            return striarray('stars', $roles);
        }
        return false;
    }
    
    /**
     * Log the user out and destroy the identity used for this session.
     * @return true if a user session was terminated, false otherwise
     */
    public static function logout()
    {
        $loggedOut = false;
        $user = self::getInstance();
        if (self::IsLoggedIn()) {
            $user->_xmlrpcClient->logout();
            $loggedOut = true;  
            // @todo actually check result coming back from xmlrpc call!  
            //       Probably need to catch exceptions and perhaps log them, but otherwise ignore them and allow logout to proceed?? Not sure.
        }
        Zend_Auth::getInstance()->clearIdentity();
        return $loggedOut;
    }
    
    /**
     * Get the XML-RPC client used by this user
     * @return STARS_XmlRpc_Client
     */
    public static function getXmlRpcClient()
    {
        $user = self::getInstance();
        return $user->_xmlrpcClient;
    }
    /**
     * Get the last message (usually after an error) generated for the user
     * @return string message
     */
    public static function getMessage()
    {
        return self::$_message;
    }
    
     /**
      *  Get the User's unique id
      *  @return personid  or 0 if user has no identity
      */
    public static function getId() 
    {
        $user = self::getInstance();
        // Careful here - anonymous users don't have personid's
        return $user->exists() ? $user->get('personid') : 0;
    }
    
    /**
      *  Get the current (default) organization for the User
      *  @return orgid  or 0 if user has no organizations
      */
    public static function getOrgid() 
    {
        $user = self::getInstance();
        // Careful here - anonymous users don't have orgid's
        return $user->exists() ? $user->get('orgid') : 0;
     }
    
    /**
      *  Get the current (default) organization for the User
      *  @return string organization name  or '' if user has no organizations
      */
    public static function getOrg() 
    {
        $user = self::getInstance();
        return $user->exists() ? $user->get('orgname') : '';
    }
    
    /**
     * Switch the organization being edited by the User
     *
     * @param STARS_PersonOrgRole $personOrgRole  Org-Role relation to select
     */
    public static function selectOrg($personOrgRole)
    {
        if ($personOrgRole->setAsDefault()) {
            self::getInstance()->_set('orgid', $personOrgRole->get('orgid'));
        }
        return true;  // only way to fail, so far, is by exception
    }
    
    /**
     * Set the given value in the User's identity
     * @param string $key Key (usually a MySQL column name)
     * @param mixed $value  value to store with this key for this person
     */
    protected function _set($key, $value)
    {
        parent::_set($key, $value);
        Zend_Auth::getInstance()->getStorage()->write($this);
    }
    
     /**
      *  Get the User's name
      *  @return name  or '' if user has no name
      */
    public static function getName() 
    {
        $user = self::getInstance();
        return $user->exists() ? $user->get('name') : '';
    }

    /**
     * Singleton : generally don't need this - access public methods above directly
     * Note: instance is defined by a call to createUser() - user with !exist() before this call
     * @return STARS_User  the user instance - always defined, !exists() if not logged in yet
     */
    public static function getInstance()
    {
        // Check if we can get the instance from Zend_Auth
        if ( Zend_Auth::getInstance()->hasIdentity() ) {
            return Zend_Auth::getInstance()->getIdentity();
        }
        // Otherwise, return unauthenticated user
        return new self(null);
    }
    
    /**
     * Check access rights for current user
     * @param integer minLevel - access level to check
     * @return true if user has access minLevel or higher, false otherwise
     */
    public static function hasAccess($minLevel)
    {
        $user = self::getInstance();
        return $user->hasAccessLevel($minLevel);
    }
    
    /**
     * Return a list of all STARS users
     *
     * @return array of users whose roles match stars*
     */
    public static function getAllUsers()
    {
            $client = self::getXmlRpcClient();
            return $client->getUsersByRole('stars');
    }
}
