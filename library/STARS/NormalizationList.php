<?php

class STARS_NormalizationList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        $options['orgid'] = issetor($options['orgid'], STARS_Person::getInstance()->get('orgid'));
        
        parent::__construct($options);
        
        $this->from(array('n' => 'datanorm'), array('n.calendaryear', 'n.datanormid', 'n.status'));
        $this->where('n.orgid = ?', $this->_options['orgid']);
        $this->order('n.calendaryear DESC');
    }
    
    public function existingYears()
    {
        $years = array();
        
        foreach($this->getList() as $row)
        {
            $years[] = $row['calendaryear'];
        }
        
        return $years;
    }
}
