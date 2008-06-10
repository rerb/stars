<?php

class STARS_NormalizationInserter extends STARS_Abstract_NormalizationWriter
{
    public function __construct(array $info)
    {
        $info['orgid'] = issetor($info['orgid'], STARS_Person::getInstance()->get('orgid'));
        
        parent::__construct($info);
    }
    
    public function write()
    {
        try
        {
            Zend_Registry::get('db')->insert('datanorm', $this->_datanorm);
        }

        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
        
        return self::SUCCESS;
    }
}
