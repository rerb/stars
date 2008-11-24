<?php
/**
 * Site Offline plugin
 * 
 * @uses Zend_Controller_Plugin_Abstract
 */
class STARS_Plugin_Offline extends Zend_Controller_Plugin_Abstract
{
    protected $_offline;
    
    /**
     * Constructor
     * 
     * @param boolean $offline  true to take site offline, false otherwise
     */
    public function __construct($offline=false)
    {
        $this->_offline = $offline;
    }

    /**
     * pre-dispatch hook:
     *  If the site is offline, then re-direct all requests to /error/offline
     *  Except for login/logout and Admin users.
     * 
     * @param  Zend_Controller_Request_Abstract $request
     */
    public function predispatch(Zend_Controller_Request_Abstract $request)
    {
        if ($this->_offline) {
          $login = ($request->getActionName() == 'login' ||
                    $request->getActionName() == 'logout') &&
                   $request->getControllerName() == 'user';
          $isAdmin = STARS_User::hasAccess(2);
          if (!$login && !$isAdmin) {
            $request->setActionName('offline')
                    ->setControllerName('error');
          }
        }
    }
}
