<?php
/**
 * Person-Org-Role List represents the list of all org-role relations one person has
 *
 */
class STARS_PersonOrgRoleList extends STARS_Abstract_SelectList
{
    public function __construct($personid, array $options = array())
    {
        parent::__construct($options);
        
        $this->from(array('r' => 'relpersons2orgs'))
             ->joinLeft(array('o' => 'organizations'), 'o.orgid = r.orgid')
             ->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'))
             ->joinLeft(array('rl'=> 'roles'), 'rl.roleid = r.roleid', array('role'))
             ->where('r.personid = ?', $personid)
             ->order('isdefault DESC')
             ->order('orgname ASC');
    }
    
    public function getAsMultiOptions()
    {
        $options = array();
        
        $rows = $this->getList();
        
        foreach($rows as $row)
        {
            $options[$row['person2orgid']] = $row['orgname'].'('.$row['role'].')';
        }
        
        return $options;
    }
}
