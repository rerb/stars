<?php
/**
 * PersonOrgRole represent one role for one person at one organization...
 *  in other words, one relation stored in the relpersons2orgs table
 */
class STARS_PersonOrgRole
{
    private $_exists;   // true if this person has an identity within STARS
    private $_info;     // array of info about this relation:
    // personid    unique user id (uid)
    // orgid       id of organization in relation
    // title       title at the organization
    // department  dept. at org.
    // roleid      role at org

    /**
     * Constructor
     * @param integer|null $id  unique id or null
     */
    public function __construct($id)
    {
        $this->_exists = false;
        $this->_info = array();
        if($id === null){
            return;
        }
        $this->_getData($id);
    }

    /**
     * Relation exists?
     * @return bool true if the relation was found in the database
     */
    public function exists()
    {
        return (bool) $this->_exists;
    }

    /**
     * Get Info from _info
     * @param string $key Key (usually a MySQL column name)
     * @return mixed or null if $key does not exist
     */
    public function get($key)
    {
        if(!$this->exists())
        {
            watchdog('defect', "Attempt to get($key) for non-existent relation", WATCHDOG_WARNING);
        }

        return issetor($this->_info[$key]);
    }

    /**
     * Get entire _info array
     * @return array
     */
    public function getAll()
    {
        if(!$this->exists())
        {
            watchdog('defect', "Attempt to get data for non-existent relation", WATCHDOG_WARNING);
        }

        return $this->_info;
    }

    /**
     * Select the given relation as the default (and unselect all others)
     *
     * @param int $personid      poid for Person to select default for
     * @param int $person2orgid  poid for PersonRoleObject to set as default
     */
    public static function selectDefault($personid, $person2orgid)
    {
        // Set all person's relations to non-default.
        $n = Zend_Registry::get('db')->update('relpersons2orgs', array('isdefault'=>0), 'personid = '.$personid);

        self::_setAsDefault($person2orgid);
    }
    
    /**
     * Delete this relation
     * @return bool true if the relation was deleted
     */
    public function delete()
    {
        if ($this->_exists) {
            $success = Zend_Registry::get('db')->delete('relpersons2orgs',
                                                        'person2orgid = '.$this->_info['person2orgid']);
            // if this is the default org - select another relation to be the default, if there is one.
            if ($success & $this->get('isdefault')) {
                self::_findDefault($this->get('personid'));
            }

            return $success;
        }
    }

    /**
     * Helper: Ensure that the given user has a default relation in the DB
     */
    protected static function _findDefault($personid)
    {
        $orgroleList = new STARS_PersonOrgRoleList($personid);
        $rows = $orgroleList->getList();

        if (count($rows) > 0) { // user still is related to at least one org...
            $id = $rows[0]['person2orgid'];     // Just choose the first one, I guess
            self::_setAsDefault($id);
        }
    }

    /**
     * Helper: Set a personOrgRole record to be the default
     *
     * @param int $id  poid for the relpersons2orgs record to update
     * @param $default true to set as default, false to unset
     */
    protected static function _setAsDefault($id, $default=true)
    {
        $n = Zend_Registry::get('db')->update('relpersons2orgs', array('isdefault'=>$default), 'person2orgid = '.$id);

        if ($n != 1) {
            watchdog('error', "Failed to update a personOrgRole: updated $n records", WATCHDOG_ERROR);
        }
    }

    /**
     * Load data about relation from DB
     * @param $id  unique id for relation to load data for
     */
    private function _getData($id)
    {
        $row = Zend_Registry::get('db')->fetchRow
        (
            'SELECT r.* FROM relpersons2orgs AS r
            WHERE (r.person2orgid = ?)',
        issetor($id, 0)
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
