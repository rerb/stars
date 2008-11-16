<?php

class STARS_Institution extends STARS_Abstract_SelectRow
{
    public function __construct($orgid)
    {
        parent::__construct();

		$this->from(array('d' => 'dataorgs'));
		$this->joinInner(array('o' => 'organizations'), 'o.orgid = d.orgid');
		$this->joinInner(array('p' => 'persons'), 'p.personid = d.personid');
		$this->joinInner(array('a' => 'dataaddresses'), 'a.addresseeid = d.personid AND a.tabletype = 2');
		$this->joinInner(array('r' => 'relpersons2orgs'), 'r.personid = d.personid');
        $this->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'));
		$this->where('d.orgid = '.intval($orgid));
    }
    
    public function getName()
    {
        $inst = $this->getData();
        if($inst != STARS_Institution::NOT_EXISTS_ERROR) {
            return $inst['orgname'];
        }
        else {
            return null;
        }
    }
    
    public function getContactData()
    {
        $array = array();
        
        if($this->getData() != STARS_Institution::NOT_EXISTS_ERROR)
        {
            $select = Zend_Registry::get('db')->select();
            $select->from('datacontactinfo');
            $select->where('contacttype IN (\'email\', \'phone\') AND tabletype = 2 AND ownerid = '.$this->get('personid'));
            $select->group('contacttype');
            $select->order('contacttype DESC');
        
            $rows = Zend_Registry::get('db')->fetchAll($select);
        }
        
        $array['contactdata'] = issetor($rows[0]['contactdata']);
        $array['contactdata2'] = issetor($rows[1]['contactdata']);
        $array['contactinfoid'] = issetor($rows[0]['contactinfoid']);
        $array['contactinfoid2'] = issetor($rows[1]['contactinfoid']);
        
        return $array;
    }
}
