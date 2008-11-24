<?php

abstract class STARS_Abstract_NormalizationWriter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;

	protected $_datanorm = array();
    
    abstract public function write();
    
    public function __construct(array $info)
    {
        $info['modifierid'] = STARS_User::getId();
        
        $this->_sortInfo($info);
    }
    
    protected function _sortInfo(array $info)
    {
        $info = STARS_Nullifier::nullify($info);
        
        foreach($info as $key => $value)
        {
            if(in_array($key, array('datanormid', 'orgid', 'calendaryear', 'status', 'boundary', 'academicstart', 'academicend', 'fiscalstart', 'fiscalend', 'residents', 'ftcommuter', 'ptcommuter', 'noncredit', 'ftfaculty', 'ptfaculty', 'ftstaff', 'ptstaff', 'acres', 'impervious', 'aircondition', 'labspace', 'medicalspace', 'budget', 'endowment', 'research', 'susfundsadminalloc', 'susfundsdiscretionary', 'susfundsfees', 'susfundsloanfund', 'normcontext', 'feedback', 'modifierid')))
            {
                $this->_datanorm[$key] = $value;
            }
		}
	}
}
