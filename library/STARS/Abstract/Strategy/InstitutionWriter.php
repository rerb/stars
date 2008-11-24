<?php

abstract class STARS_Abstract_Strategy_InstitutionWriter
{
    protected $_dataaddresses = array();
    protected $_datacontactinfo = array();
    protected $_datacontactinfo2 = array();
    protected $_dataorgs = array();
    protected $_persons = array();
    protected $_relpersons2orgs = array();
    
    public function __construct(array $info)
    {
        $this->_datacontactinfo = array
        (
            'contacttype' => 'phone',
            'tabletype' => 2
        );
        
        $this->_datacontactinfo2 = array
        (
            'contacttype' => 'email',
            'tabletype' => 2
        );
        
        $this->_dataaddresses = array
        (
            'diaddresstype' => 171,
            'tabletype' => 2
        );
        
        $info['modifierid'] = STARS_User::getId();
        
        $this->_sortInfo($info);
    }
    
    abstract public function write();
    
    /**
     * @todo modifierid
     */
    protected function _sortInfo(array $info)
    {
        $info = STARS_Nullifier::nullify($info);
        
        foreach($info as $key => $value)
        {
            if(in_array($key, array('addressid','addresseeid', 'diaddresstype', 'address1', 'address2', 'address3', 'city', 'state', 'postalcode', 'country', 'modifierid')))
            {
                $this->_dataaddresses[$key] = $value;
            }

            if(in_array($key, array('orgid', 'dicarnegieclass','greenwebsite', 'founding', 'personid','instcontext', 'modifierid')))
            {
                $this->_dataorgs[$key] = $value;
            }
  
            if(in_array($key, array('personid', 'firstname', 'middlename', 'lastname', 'modifierid')))
            {
                $this->_persons[$key] = $value;
            }

            if(in_array($key, array('orgid', 'personid', 'title', 'department', 'modifierid')))
            {
                $this->_relpersons2orgs[$key] = $value;
            }

            if(in_array($key, array('contactinfoid', 'ownerid', 'contacttype', 'contactdata', 'modifierid')))
            {
                $this->_datacontactinfo[$key] = $value;
            }

            if(in_array($key, array('contactinfoid2', 'ownerid2', 'contacttype2', 'contactdata2')))
            {
                $this->_datacontactinfo2[substr($key, 0, -1)] = $value;
            }
            
            $this->_datacontactinfo2['modifierid'] = $info['modifierid'];
		}
	}
}
