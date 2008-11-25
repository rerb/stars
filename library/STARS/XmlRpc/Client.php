<?php
/**
 * STARS/XmlRpc/Client.php
 * 
 * @author J. Fall 
 * @version 0.1
 * @package STARS
 */

/**
 * STARS_XmlRpc_Client
 *
 * Extended XmlRpc Client services for STARS
 * Provides access to remote procedure calls,
 *  primarily inteded for use with the Drupal Resource Center
 * Each of the methods may throw several types of Zend_XmlRpc_Exception if something goes wrong.
 */
class STARS_XmlRpc_Client extends Zend_XmlRpc_Client
{

  // TO DO: these should be in config main.ini
  const DEFAULT_SERVER = 'http://drupalsandbox.aashedev.org/services/xmlrpc';
//  const SERVER_KEY = '6d1d181fe731e5c1acf55ec2c2de0103';   // stars.local
  const SERVER_KEY = '5067330c02e76b4bd34d45afde74757c';     // dev.starstracker.aashe.org
  const USE_KEY = true;
  const USE_SESSID = true;
  private $_sessionid;     // the sessionid retrieved during authentication.
  
  /**
   * Construct a new XmlRpc Client.
   * @param $server  string URL for server or null for default server
   */
  public function __construct($server=null)
  {
    if ($server == null) {
      $server = self::DEFAULT_SERVER;
    }
    parent::__construct($server);
    $this->_sessionid = Zend_Session::getId();
  }

  /**
   * Authenticate to the server with given info.
   *
   * @param $username string User's login id on the server
   * @param $password string User's p/w on the server
   *
   * @return RPC result returned by server
   */
  public function login($username, $password)
  {
     $result = $this->call('user.login', array($username, $password));
     if (self::USE_SESSID) {
         $this->_sessionid = $result['sessid'];
     }
     return $result['user'];
  }

  /**
   * Logout this client's session from the remote server.
   *
   * @return RPC result returned by server
   */
  public function logout()
  {
     return $this->call('user.logout', array());
  }
  
  /**
   * Get info about a user.
   *
   * @param $user string User's login name or user id on the server
   *
   * @return RPC result returned by server
   */
  public function getUser($user)
  {  
     if (is_numeric($user)) {
     	return $this->call('user.get', array((int)$user));
     }
     else {
     	return $this->call('user.get-byname', array($user));
     }
  }

  /**
   * Get list of users based on their role.
   *
   * @param $role string  STARS_user or STARS_admin
   *
   * @return RPC result returned by server
   */
  public function getUsersByRole($role)
  {    
     return $this->call('user.listbyrole', array($role));
  }

  /**
   * Get list of users based on their user name.
   *
   * @param $name string  first few characters in user's name
   *
   * @return RPC result returned by server
   */
  public function getUsersByName($name)
  {    
     return $this->call('user.get-listbyname', array($name));
  }


  /**
   * Helper: make the RPC call and return the results.
   *
   * @param $function string name of the RPC function to be called.
   * @param $args     array of arguments to the RPC
   *
   * @return RPC result returned by server
   */
  public function call($function, $args)
  {
     $params = $this->_getParams($function);
     
     $params  = array_merge($params, $args);
     
     return parent::call($function, $params);
  }

  /** 
   * Helper:  set-up the parameters for the RPC
   *
   * @param $function string name of the RPC function to be called.
   * @return the basic array of parameters required to make any RPC
   */
  private function _getParams($function)
  {
    if (self::USE_KEY) {
      $thisServer = $_SERVER['SERVER_NAME'];
      $key = self::SERVER_KEY;

      $timestamp = ''.time();
      srand();
      $nonce = md5( uniqid( rand(), true ) );

      $hash_parameters = array($timestamp, $thisServer, $nonce, $function);
      $hash = hash_hmac("sha256", implode(';', $hash_parameters), $key);
      $params = array(
                $hash,
                $thisServer,
                $timestamp,
                $nonce,
             );
    }
    else {
      $params = array();
    }
    if (self::USE_SESSID) {
        $params[] = $this->_sessionid;
    }  
    return $params;
  }
}