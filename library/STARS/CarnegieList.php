<?php

class STARS_CarnegieList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        $this->from(array('d' => 'dataitems'), array('groupname', 'itemid', 'itemdisplay'));
        $this->where('groupname = ?', 'carnegieclass');
        $this->order('itemdisplay ASC');
    }

    
    public function getAsMultiOptions()
    {
        $options = array();
        
        $rows = $this->getList();
        
        foreach($rows as $row)
        {
            $options[$row['itemid']] = $row['itemdisplay'];
        }
        
        return $options;
    }
}
