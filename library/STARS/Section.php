<?php

class STARS_Section
{
    private $_credits = array();
    private $_sectionId;
    
    /**
     * Section is really just a list of credits of one type (OP, AF, ER, etc.)
     * It is always built for a particular sectionId, in which case it is either
     *  organization neutral for anon. users, or specific to users organizatrion;
     * but it can also be built for a particular orgId to allow administrators to
     *  access credit information for any enrolled organization.
     * Currently, sections without credits are badly broken beasts - easy to fix
     *  in future, a section can stand alone, and HAVE A credit list.
     * @param $sectionId required section to get credits for 
     * @param $orgId optional organization to get credits for (current user if null)
     * 
     **/
    public function __construct($sectionId, $orgId = null)
    {
        $this->_sectionId = intval($sectionId);
        
        $this->_retrieveCredits( intval($orgId) );
    }
    
    public function getCredits()
    {
        return $this->_credits;
    }

    /**
     * Get summary information about credits in each section
     * @return array of summary info about each section.
     */
    static public function sectionSummary()
    {
        try
        {
            $summary = Zend_Registry::get('db')->fetchAll
            (
               'SELECT COUNT(*) AS credits, c.dicreditcategory, di.itemdisplay AS sectiontitle, di.itemvalue AS sectionabbr
                FROM credits AS c 
                LEFT JOIN (dataitems AS di)
                ON (c.dicreditcategory = di.itemid)
                GROUP BY c.dicreditcategory
                ORDER BY dicreditcategory ASC',
                array(),
                Zend_Db::FETCH_ASSOC
            );
            return $summary;
        }
        catch(Zend_Db_Exception $e) {}
    }

    /**
     *  Required b/c Section is a Transaction Script object rather than a Domain Model.
     */
    public function getSectionInfo()
    {
        return array(
                     'id' => $this->getID(),
                     'title' => $this->getTitle(),
                    );
    }

    public function getID()
    {
        return $this->_sectionId;
    }

    public function getTitle()
    {
        if(count($this->_credits) > 0)
        {
            return $this->_credits[0]['sectiontitle'];
        }
        
        return '';
    }

  /**
   * Get status information about this Section (list of credits).
   * @to-do - this belongs in the missing "CreditList" class
   * @return array of status information about this Section's credits.
   */
    public function getStatus()
    {
        $credits = $this->getCredits();
        $status = array();
        $status['complete'] = false;
        $numCredits = count($credits);
        $numComplete = $this->creditsComplete();
        
        if ($numComplete == 0) {
          $status['msg'] = "Incomplete";
          $status['stats'] = "$numCredits Credits to be submitted";
        }
        else if ($numComplete == $numCredits) {
          $status['msg'] = "Complete";
          $status['stats'] = "All $numCredits Credits have been submitted";
          $status['complete'] = true;
        }
        else { // 0 < $numComplete < $numCredits
          $status['msg'] = "Partially Complete";
          $status['stats'] = "$numComplete of $numCredits Credits submitted";
        }
        $status['numCredits'] = $numCredits;
        $status['numComplete'] = $numComplete;
        return $status;
    }
    
  /**
   * How many of the credits in this Section are compete?
   * @to-do - this belongs in the missing "CreditList" class
   * @return integer number of credits that are completed.
   */
    public function creditsComplete()
    {
        $credits = $this->getCredits();
        $count = 0;
        foreach ($credits as $credit) {
          // Previous Submission for this credit
          if (! empty($credit['status']) ) {
             $count++;
          }
        }
        return $count;
    }
    
    private function _retrieveCredits($orgId = null)
    {
        $user = STARS_Person::getInstance();
        if ($orgId == null && $user->exists()) {
          $orgId = $user->get('orgid');
        }
        
        try
        {
          // Conditional query was needed to report credit information to anon. users
          // This is not needed until this functionality is implemented... but got
          //   added during development due to changing requirements...
          // TO DO: change this to build query conditionally.
          if ($user->exists()) {
            $this->_credits = Zend_Registry::get('db')->fetchAll
            (
                'SELECT o.*, c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, di2.itemdisplay AS subsectiontitle, di2.itemvalue as subsectionname
                FROM credits AS c
                INNER JOIN (dataitems AS di1)
                ON (c.dicreditcategory = di1.itemid)
                LEFT JOIN (dataitems AS di2)
                ON (c.dicreditsubcategory = di2.itemid)
                LEFT JOIN (orgcreditfiles AS o)
                ON (c.creditid = o.creditid AND o.orgid = ?)
                WHERE c.dicreditcategory = ?
                ORDER BY credittype=\'1\' DESC,
                         c.dicreditsubcategory ASC, 
                         credittype ASC, creditnumber ASC',
                array($orgId, $this->_sectionId),
                Zend_Db::FETCH_ASSOC
            );
          }
          else {
            $this->_credits = Zend_Registry::get('db')->fetchAll
            (
                'SELECT c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, di2.itemdisplay AS subsectiontitle, di2.itemvalue as subsectionname
                FROM credits AS c
                INNER JOIN (dataitems AS di1)
                ON (c.dicreditcategory = di1.itemid)
                LEFT JOIN (dataitems AS di2)
                ON (c.dicreditsubcategory = di2.itemid)
                WHERE c.dicreditcategory = ?
                ORDER BY credittype=\'1\' DESC, 
                         c.dicreditsubcategory ASC, 
                         credittype ASC, creditnumber ASC',
                array($this->_sectionId),
                Zend_Db::FETCH_ASSOC
            );
          }
        }
        
        catch(Zend_Db_Exception $e) {}
    }
}
