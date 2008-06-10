<?php

class STARS_PasswordResetter
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;
    const KEY_ERROR = -2;
    
    private $_info;
    private $_keyId;
    
    public function __construct(array $info)
    {
        $this->_info = $info;
    }
    
    public function reset()
    {
        try
        {
            $this->_getIds();
            $this->_updateUser();
            $this->_deleteKey();
        }
        
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            return self::OTHER_ERROR;
        }
        
        catch(STARS_Exception $e)
        {
            return self::KEY_ERROR;
        }
        
        return self::SUCCESS;
    }
    
    /**
     * @throws Zend_Db_Statement_Mysqli_Exception
     */
    private function _deleteKey()
    {
        Zend_Registry::get('db')->delete('passwordresetkeys', 'keyid = '.$this->_keyId);
    }
    
    /**
     * @throws STARS_Exception
     */
    private function _getIds()
    {
        $select = Zend_Registry::get('db')->select();
        $select->from(array('d' => 'datasecurity'), 'd.personid');
        $select->joinInner(array('p' => 'passwordresetkeys'), 'p.securityid = d.securityid', array('p.keyid'));
        $select->where('p.key = ? AND d.username = ? AND p.datemodified >= ?', array
        (
            $this->_info['key'],
            $this->_info['username'],
            new Zend_Db_Expr('DATE_SUB(CURDATE(), INTERVAL 7 DAY)')
        ));
        
        $row = Zend_Registry::get('db')->fetchRow($select);
        
        if($row == null)
        {
            throw new STARS_Exception('Key is invalid.');
        }

        $this->_info['personid'] = $row['personid'];
        $this->_keyId = $row['keyid'];
    }
    
    /**
     * @throws Zend_Db_Statement_Mysqli_Exception
     */
    private function _updateUser()
    {
        $updater = new STARS_UserUpdater($this->_info);
        $updater->write();
    }
}
