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
     * pre-dispatch hook
     * 
     * @param  Zend_Controller_Request_Abstract $request
     */
    public function predispatch(Zend_Controller_Request_Abstract $request)
    {
        if ($this->_offline) {
          $request->setActionName('offline')
                  ->setControllerName('error');
        }
    }
}
