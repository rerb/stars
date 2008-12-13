<?php

/**
 * Watchdog is a logging system based on Drupal's model.
 * The actual watchdog function lives in the global functions.php -
 *    it is used to create entries in the watchdog DB table.
 * This controller provides an admin interface to the watchdog table and settings.
 * Here's some things we could do in future:
 *  - allow the parameters currently specified as constants below, to be adjusted through interface
 *  - allow watchdog report to be searchable on various criteria, like userid, type, severity, etc.
 *  - add a pager
 */

define('WATCHDOG_EXPIRE', 7);  // # days after which watchdog entries to expire

class WatchdogController extends STARS_ActionController
{
    /**
     * Index action: List the contents of the Watchdog table
     */
    public function indexAction() 
    {
        $this->_protect(2);
        
        $entryList = new STARS_WatchdogList();
        
        $this->view->list = $entryList->getList();
    }

    /**
     * Display log entry details action: List all details for a specific log entry
     *   - parameter watchdogid for the entry is passed in the request
     */
    public function entryAction() 
    {
        $this->_protect(2);
        
        $id = $this->_getParam('number');
        $entry = new STARS_WatchdogEntry($id);
        $this->view->entry = $entry->getData();
    }
    
    /**
     * Remove expired log messages.
     *  - intended to eventually be called from a cron job
     */
    public function clearlogAction() 
    {
        $this->_protect(2);
        try {
            $n = Zend_Registry::get('db')->delete('watchdog', 'timestamp < DATE_SUB(CURRENT_DATE, 
                                                                       INTERVAL '.WATCHDOG_EXPIRE.' DAY)');
            if ($n > 1) { 
                watchdog('watchdog','Log cleared');
            }
            $this->_flashMessage("$n expired messages cleared from Watchdog log.");
        }
        catch (Exception $e) {
            watchdog('DB','Error clearing log: '.$e->getMessage(), WATCHDOG_ERROR);
            $this->_flashMessage("Internal Error: Watchdog log could not be cleared.");
        }
       $this->_redirect('/watchdog/');
    }
}
