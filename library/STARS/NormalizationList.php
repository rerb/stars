<?php

class STARS_NormalizationList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        $options['orgid'] = issetor($options['orgid'], STARS_User::getOrgid());
        
        parent::__construct($options);
        
        $this->from(array('n' => 'datanorm'), array('n.calendaryear', 'n.datanormid', 'n.status'));
        $this->where('n.orgid = ?', $this->_options['orgid']);
        $this->order('n.calendaryear DESC');
    }
    
    public function existingYears()
    {
        $years = array();
        
        foreach($this->getList() as $row)
        {
            $years[] = $row['calendaryear'];
        }
        
        return $years;
    }

  /**
   * Get information about this Normalization list
   * Assumes the list is ordered by calendaryear, descending
   * @return array of information ('numYears', 'yearsComplete', 'isComplete')
   */
    public function getInfo()
    {
      $list = $this->getList();
      $info = array();
      $info['numYears'] = count($list);
      $completeYears = array();
      foreach($list as $year) {
        if($year['status'] == STARS_STATUS_COMPLETE) {
          $completeYears[] = $year['calendaryear'];
        }
      }
      $info['yearsComplete'] = count($completeYears);
      $info['isComplete'] =($info['yearsComplete'] >= 3) &&  // short-cut evaluation
                           $this->_isComplete($completeYears);
      if ($info['numYears'] > 0) {
        $info['msg'] = "Partially Complete";
        $info['stats'] = "{$info['yearsComplete']} of {$info['numYears']} years completed.";
      }
      else {
        $info['msg'] = "Incomplete";
        $info['stats'] = "No normalization data has been submitted";
      }
      if ($info['isComplete']) {
        $info['msg'] = "Complete";
      }
      return $info;
    }
  
  /**
   * Helper: determine if a list of years represents a complete set
   *         of Normalization submissions
   * @param competeYears array of year numbers that have been completed
   *   PRE: assumes count(competeYears)>0 & is sorted in descending order!
   * @return true if Normalization List is a complete set, false otherwise
   */
  private function _isComplete($completeYears)
  {
    // Normalization List is complete if any 3 consecutive years are complete.
    $consecYears = 1;
    $prevYear = issetor($completeYears[0]);
    foreach ($completeYears as $year) {
      if ($prevYear-1 == $year)
        $consecYears++;
      else
        $consecYears=1;
      if ($consecYears >= 3) {
        return true;
      }
      $prevYear = $year;
    }
    return false;
  }
}
