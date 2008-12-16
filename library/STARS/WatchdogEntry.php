<?php
/**
 * All details for one entry in the Watchdog log
 *
 */
class STARS_WatchdogEntry extends STARS_Abstract_SelectRow
{
    protected $_person;
    
    /**
     * Construct query for one entry
     *
     * @param int $watchdogid  poid for the entry
     */
    public function __construct($watchdogid)
    {
        parent::__construct();

		$this->from(array('w' => 'watchdog'))
//		     ->joinLeft(array('p' => 'persons'), 'p.personid = w.personid')
		     ->joinLeft(array('r' => 'relpersons2orgs'), 'r.personid = w.personid')
		     ->joinLeft(array('o' => 'organizations'), 'o.orgid = r.orgid')
		     ->joinLeft(array('rl' => 'roles'), 'rl.roleid = r.roleid')
		     ->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'))
		     ->where('w.watchdogid = '.intval($watchdogid));
		$this->_person = null;
    }

    /**
     * Override getData method to add person details (which are not stored in the STARS DB)
     *
     * @return array of data about this watchdog entry
     */
    public function getData()
    {
        if (parent::getData() != self::NOT_EXISTS_ERROR && $this->_person == null) {
            $this->_person = STARS_Person::factory($this->_row['personid']);
            foreach ($this->_person->getAll() as $field => $value) {   
                $this->_row[$field] = $value;
            }
        }
        return ($this->_row === null) ? self::NOT_EXISTS_ERROR : $this->_row;
    } 
}
