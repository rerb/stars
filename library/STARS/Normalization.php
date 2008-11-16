<?php

class STARS_Normalization extends STARS_Abstract_SelectRow
{
    public function __construct($datanormid)
    {
        parent::__construct();
        
        $this->from('datanorm');
        $this->where('datanormid = ?', intval($datanormid));
    }
    
  /**
   * Fectch all normalization record. (this is a domain model method - doesn't really fit)
   * @return an array containing all normalization records by organization
   *         or null if there was an error.
   */
  static public function getAllRecords()
  {
    try {
      $normRecs = Zend_Registry::get('db')->fetchAll
      (
        'SELECT
           i.fullname AS orgname,  n.* 
         FROM organizations o
         LEFT JOIN aashedata01.institutionnames i
         ON o.nameid = i.id 
         LEFT JOIN datanorm n
         ON o.orgid  = n.orgid   
         ORDER BY orgname ASC, n.calendaryear DESC',
         array(),
         Zend_Db::FETCH_ASSOC
      );

      return $normRecs;
    }
    catch(Zend_Db_Exception $e) { return null;}
  }    
}
