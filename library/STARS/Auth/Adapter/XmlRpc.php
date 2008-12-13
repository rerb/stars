<?php
/**
 * STARS_Auth_Adapter_XmlRpc.php
 * @author  J. Fall
 * @version 0.1
 * @package STARS 
 */
/**
 * XML Remote Procedure Call Authentication Adapter class
 * Authenticates to an XML-RPC server defined by the XmlRpc_Client.
 *
 */
class STARS_Auth_Adapter_XmlRpc implements Zend_Auth_Adapter_Interface
{
     private $_username;
     private $_password;
     private $_client;    // remote  XMLRpc client to authenticate to
     
    /**
     * Sets username and password for authentication
     *
     * @return void
     */
    public function __construct($username, $password)
    {
        $this->_username = $username;
        $this->_password = $password;
        $this->_client = null;
    }

    /**
     * Performs an authentication attempt
     *
     * @throws Zend_Auth_Adapter_Exception If authentication cannot
     *                                     be performed
     * @todo add error handling for case were user authenticates, but has no specific permissions in STARS.
     * @return Zend_Auth_Result with the STARS_User instance as the identity.
     */
    public function authenticate()
    {
        $this->_client = new STARS_XmlRpc_Client();
        try {
            $result = $this->_client->login($this->_username, $this->_password);
            
            return new Zend_Auth_Result(Zend_Auth_Result::SUCCESS, $result);
        }
        // A client fault can be anything that goes wrong with the response, anything from a
        //  server configuration error to invalid user name or password.
        // We want to distinguish just 2 cases: Server/Network error vs. Authentication error.
        // Only way to do it is to look at the message returned from the RPC. 
        catch (Exception $e) {   
          watchdog('XML-RPC', $e->getMessage(), WATCHDOG_NOTICE);
          if (is_a($e, 'Zend_XmlRpc_Client_FaultException') &&
              stripos($e->getMessage(),'password') !== false) {   // hackish way to ID invalid credential
              return new Zend_Auth_Result(Zend_Auth_Result::FAILURE_IDENTITY_NOT_FOUND, $this->_username); 
          }
          else  {  // anything else indicates an http, server, network error.
              return new Zend_Auth_Result(Zend_Auth_Result::FAILURE, $this->_username); 
          }
        }
    }
    
    /**
     * Get the XML-RPC client used for the authentication.
     * This client should be used for all subsequent XML-RPC requests.
     *
     * @return STARS_XmlRpc_Client
     */
    public function getXmlRpcClient()
    {
        return ($this->_client==null) ? (new STARS_XmlRpc_Client()) : ($this->_client);
    }
}
