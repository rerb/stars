<?php
/**
 * All details for one entry in the Watchdog log
 *
 */
class STARS_WatchdogEntry extends STARS_Abstract_SelectRow
{
    /**
     * Construct query for one entry
     *
     * @param int $watchdogid  poid for the entry
     */
    public function __construct($watchdogid)
    {
        parent::__construct();

		$this->from(array('w' => 'watchdog'))
		     ->joinLeft(array('p' => 'persons'), 'p.personid = w.personid')
		     ->joinLeft(array('r' => 'relpersons2orgs'), 'r.personid = w.personid')
		     ->joinLeft(array('o' => 'organizations'), 'o.orgid = r.orgid')
		     ->joinLeft(array('rl' => 'roles'), 'rl.roleid = r.roleid')
		     ->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'))
		     ->where('w.watchdogid = '.intval($watchdogid));
    }
}
