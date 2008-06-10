<?php

class STARS_UserList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        $this->from(array('p' => 'persons'), array('p.personid', 'p.firstname', 'p.lastname'));
        $this->joinInner(array('d' => 'datasecurity'), 'p.personid = d.personid', array('d.username', 'd.level'));
        $this->joinLeft(array('r' => 'relpersons2orgs'), 'p.personid = r.personid', array('r.orgid'));
        $this->joinLeft(array('o' => 'organizations'), 'o.orgid = r.orgid');
        $this->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', array('orgname' => 'n.fullname'));
        $this->order(array('level DESC', 'username ASC'));
    }
}
