<?php

class STARS_Strategy_InstitutionInserter extends STARS_Abstract_Strategy_InstitutionWriter
{
    public function write()
    {
        try
        {
            Zend_Registry::get('db')->insert('persons', $this->_persons);
            
            $personid = Zend_Registry::get('db')->lastInsertId();
            $this->_relpersons2orgs['personid'] = $personid;
            $this->_dataorgs['personid'] = $personid;
            $this->_dataaddresses['addresseeid'] = $personid;
            $this->_datacontactinfo['ownerid'] = $personid;
            $this->_datacontactinfo2['ownerid'] = $personid;
            
            Zend_Registry::get('db')->insert('dataorgs', $this->_dataorgs);
            
            Zend_Registry::get('db')->insert('dataaddresses', $this->_dataaddresses);
            
            Zend_Registry::get('db')->insert('relpersons2orgs', $this->_relpersons2orgs);

			Zend_Registry::get('db')->insert('datacontactinfo', $this->_datacontactinfo);
			
			Zend_Registry::get('db')->insert('datacontactinfo', $this->_datacontactinfo2);
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            echo $e->getMessage();
            
            return STARS_InstitutionWriter::OTHER_ERROR;
        }
        
        return STARS_InstitutionWriter::SUCCESS;
    }
}
