<?php

class STARS_RoleList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        $this->from(array('r' => 'roles'));
        $this->order('roleid ASC');
    }
    
    public function getAsMultiOptions()
    {
        $options = array();
        
        $rows = $this->getList();
        
        foreach($rows as $row)
        {
            $options[$row['roleid']] = $row['role'];
        }
        
        return $options;
    }
}
