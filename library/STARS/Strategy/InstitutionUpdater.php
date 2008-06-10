<?php

class STARS_Strategy_InstitutionUpdater extends STARS_Abstract_Strategy_InstitutionWriter
{
    public function write()
    {
        try
        {
            Zend_Registry::get('db')->update('dataorgs', $this->_dataorgs, 'orgid = '.intval($this->_dataorgs['orgid']));
            
            Zend_Registry::get('db')->update('persons', $this->_persons, 'personid = '.intval($this->_persons['personid']));

            Zend_Registry::get('db')->update('dataaddresses', $this->_dataaddresses, 'addressid = '.intval($this->_dataaddresses['addressid']));

            Zend_Registry::get('db')->update('datacontactinfo', $this->_datacontactinfo, 'contactinfoid = ' .intval($this->_datacontactinfo['contactinfoid']));

			Zend_Registry::get('db')->update('datacontactinfo', $this->_datacontactinfo2, 'contactinfoid = ' .intval($this->_datacontactinfo2['contactinfoid']));
			
			Zend_Registry::get('db')->update('relpersons2orgs', $this->_relpersons2orgs, 'personid = ' .intval($this->_persons['personid']).' AND orgid = '.intval($this->_dataorgs['orgid']));
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return STARS_InstitutionWriter::OTHER_ERROR;
        }
        
        return STARS_InstitutionWriter::SUCCESS;
    }
}
