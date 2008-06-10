<?php

class STARS_NormalizationUpdater extends STARS_Abstract_NormalizationWriter
{
    public function write()
    {
        try
        {
            Zend_Registry::get('db')->update('datanorm', $this->_datanorm, 'datanormid = '.intval(issetor($this->_datanorm['datanormid'], 0)));
        }

        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
        
        return self::SUCCESS;
    }
}
