<?php

class STARS_OrganizationList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        $this->from(array('o' => 'organizations'), array('orgid')); //removed parentorgid
        $this->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', new Zend_Db_Expr('n.fullname AS orgname'));
        $this->order('orgname ASC');
    }
    
    public function getAsMultiOptions()
    {
        $options = array();
        
        $rows = $this->getList();
        
        foreach($rows as $row)
        {
            $options[$row['orgid']] = $row['orgname'];
        }
        
        return $options;
    }
}
