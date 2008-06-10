<?php

class STARS_PasswordResetEmailer
{
    const SUCCESS = 1;
    const OTHER_ERROR = -1;
    const NOT_EXISTS_ERROR = -2;
    
    private $_securityid;
    private $_username;
    
    public function __construct($username)
    {
        $this->_username = $username;
    }
    
    public function sendLink()
    {
        if(!$this->_usernameExists())
        {
            return self::NOT_EXISTS_ERROR;
        }
        
        try
        {
            $mail = new STARS_Mail;
            $mail->addTo($this->_username);
            $mail->setSubject('STARS Password Reset');
            $mail->setBodyTemplate('../emails/passwordreset.txt', array
            (
                '<link>' => $this->_createLink()
            ));
            $mail->send();
            
            return self::SUCCESS;
        }
        
        catch(Exception $e) // I don't care what kind.
        {
            return self::OTHER_ERROR;
        }
    }
    
    private function _createLink()
    {
        $hash = md5(microtime().'lololololololololololololololololol');
        
        Zend_Registry::get('db')->insert('passwordresetkeys', array
        (
            'securityid' => $this->_securityid,
            'key' => $hash
        ));
        
        return 'http://'.$_SERVER['SERVER_NAME'].'/password/reset/'.$hash.'/';
    }
    
    private function _usernameExists()
    {
        $id = Zend_Registry::get('db')->fetchOne('SELECT securityid FROM datasecurity WHERE username = ?', $this->_username);
        
        if($id === false)
        {
            return false;
        }
        
        $this->_securityid = $id;
        
        return true;
    }
}
