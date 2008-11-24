<?php

class STARS_Abstract_SelectList extends Zend_Db_Select
{
    private $_list = array();
    protected $_options = array();
    
    public function __construct(array $options = array())
    {
        parent::__construct(Zend_Registry::get('db'));
        
        $this->_options = $options;

        $this->limitPage(issetor($this->_options['page'], 1), issetor($this->_options['perpage'], 1000));
    }
    
    public function getList()
    {
        if(count($this->_list) == 0)
        {
            try
            {
                $this->_list = Zend_Registry::get('db')->fetchAll($this->__toString(), array(), Zend_Db::FETCH_ASSOC);
            }
            
            catch(Zend_Db_Statement_Mysqli_Exception $e) { }
        }
        return $this->_list;
    }
}
