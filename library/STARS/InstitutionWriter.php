<?php

/**
 * I'm pretty sure the so-called strategies used here are 
 * bastardized versions of the real pattern.
 */
class STARS_InstitutionWriter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;

    private $_info = array();
    private $_strategy;
    
    public function __construct(array $info)
    {
        $info['orgid'] = issetor($info['orgid'], STARS_User::getOrgid());
        
        $this->_info = $info;
        
        $this->_existingData();
    }
    
    public function write()
    {
        return $this->_strategy->write();
    }
    
    /**
     * Checks for existing data, sets strategy, and IDs if they exist
     */
    private function _existingData()
    {
        $institution = new STARS_Institution($this->_info['orgid']);
        
        if(($data = $institution->getData()) === STARS_Institution::NOT_EXISTS_ERROR)
        {
            $this->_setStrategy(new STARS_Strategy_InstitutionInserter($this->_info));
            return;
        }
        
        $contactdata = $institution->getContactData();
        
        $this->_info['personid'] = $data['personid'];
        $this->_info['addresseeid'] = $data['personid'];
        $this->_info['addressid'] = $data['addressid'];
        $this->_info['contactinfoid'] = $contactdata['contactinfoid'];
        $this->_info['contactinfoid2'] = $contactdata['contactinfoid2'];
        
        $this->_setStrategy(new STARS_Strategy_InstitutionUpdater($this->_info));
    }
    
    private function _setStrategy(STARS_Abstract_Strategy_InstitutionWriter $strategy)
    {
        $this->_strategy = $strategy;
    }
}
