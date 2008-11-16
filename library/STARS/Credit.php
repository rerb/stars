<?php
/**
 * Stars Credit
 *
 * @category Model
 * @package STARS
 * @author  J. Fall
 */
define('STARS_CREDIT_CREDIT', 0);
define('STARS_CREDIT_PREREQ', 1);
define('STARS_CREDIT_TT', 2);
 
/**
 * STARS_Credit
 * Domain Model representing a Stars Credit.
 * Also acts as a DB Mapper for the credits table.
 */
class STARS_Credit
{
  private $_record;
  private $_creditOID;

  /**
   * Construct a new Credit for the persistent object
   * @param integer $creditId  POID for the credit to construct
   */
  public function __construct($creditId)
  {
    $this->_creditOID = intval($creditId);
    $this->_record = null;  // using lazy read
  }

  /**
   * Is this Credit specified?
   * @return true if the Credit has a definition, false otherwise
   */
  public function isValidCredit()
  {
    $credit = $this->getCreditInfo();
    return ( count($credit) > 0 );
  }

  /**
   * Get the Persistent Object ID for this Credit
   * @return integer POID or null
   */
  public function getId()
  {
    $credit = $this->getCreditInfo();
    return $credit['creditid'];
  }

  /**
   * Get the credit number for this Credit
   * @return integer credit number
   */
  public function getCreditNumber()
  {
    $credit = $this->getCreditInfo();
    return $credit['creditnumber'];
  }


  /**
   * Get the points available for this Credit
   * @return integer points available or null
   */
  public function getPointsAvailable()
  {
    $credit = $this->getCreditInfo();
    return $credit['pointsavailable'];
  }

  /**
   * Get the title for this Credit 
   * @return string  (e.g., "Credit AF6" or "Prerequisit OP1")
   */
  public function getTitle()
  {
    if($this->isValidCredit()) {
      if ($this->isPrereq()) {
        $title = " Prerequisite " . $this->_record['creditnumber'].
                             ': ' . $this->_record['creditname'];
      }
      else if ($this->isTier2()) {
        $title = $this->_record['subsectiontitle'] .
                 ": Tier Two Credits";
      }
      else {
        $title = "Credit  ".$this->_record['sectionabbr'].
                            $this->_record['creditnumber'].
                     ': ' . $this->_record['creditname'];
      }
      return $title;
    }

    return '';
  }
  
  /**
   * Get information about this credit's section
   *  Required b/c Section is a Transaction Script object rather than a Domain Model.
   * @return array of strings describing the section ('id', 'title')
   */
  public function getSectionInfo()
  {
    return array(
                 'id' => $this->getSectionID(),
                 'title' => $this->getSectionTitle(),
                );
  }

  /**
   * Get Category ID for this Credit
   * @return integer
   */
  public function getSectionId()
  {
    $credit = $this->getCreditInfo();
    return $credit['dicreditcategory'];
  }

  /**
   * Get Category abbreviation for this Credit
   * @return integer
   */
  public function getSectionAbbr()
  {
    $credit = $this->getCreditInfo();
    return $credit['sectionabbr'];
  }

  /**
   * Get the section title for this Credit 
   * @return string  (e.g., "Adiministration and Finance")
   */
  public function getSectionTitle()
  {
    if($this->isValidCredit()) {
      return $this->_record['sectiontitle'];
    }
    return '';
  }


  /**
   * Is this Credit actually a pre-requisite?
   * @return true if it is a pre-req, false otherwise
   */
  public function isPrereq()
  {
    if($this->isValidCredit()) {
      return $this->_record['credittype'] == STARS_CREDIT_PREREQ;
    }

    return '';
  }
  
  /**
   * Is this Credit a tier-two credit?
   * @return true if it is a TT, false otherwise
   */
  public function isTier2()
  {
    if($this->isValidCredit()) {
      return $this->_record['credittype'] == STARS_CREDIT_TT;
    }

    return '';
  }

  /**
   * Get the record for this Credit PDO
   * @return array with DB fields as keys, or empty array
   */
  public function getCreditInfo()
  {
    // Lazy read - load here if credit info not loaded yet.
    if ($this->_record == null) {
      $this->_record = $this->_retrieveRecord($this->_creditOID);
    }

    if ( $this->_isValidRecord($this->_record) ) {
      return $this->_record;
    }
    else {
      return array();
    }
  }

  /**
   * Helper: is the credit record valid for this PDO?
   * @param array $credit data array for a credit.
   */
  private function _isValidRecord($record)
  {
    return (is_array($record)  && 
            $record['creditid'] == $this->_creditOID );
  }


  /**
   * Build the CSV file name for this credit's merged PDF data file.
   * @return string filename (NOT full path) for the CSV data file for this credit.
   */
  public function csvFilename()
  {
    $filename = $this->creditCode('_') . '.csv';
    return $filename;
  }
  /**
   * Build the CSV file name for this credit's export data file.
   * @return string filename (NOT full path) for the export CSV file for this credit.
   */
  public function exportFilename()
  {
    $filename = $this->creditCode('_') . '_export.csv';
    return $filename;
  }
  /**
   * Export all of the data answers for this credit to a CSV file
   */
  public function export()
  {
     $questions = $this->_retrieveQuestions($this->getId());
     array_unshift($questions, "Institution", "Points");
     $answers = $this->_retrieveAnswers($this->getId());
     $org = '';
     $rec = array();
     foreach ($answers as $answer) {
       if ($answer['orgname'] != $org) {
         $org = $answer['orgname'];
         $rec[$org] = array('orgname'=>$org);
         $rec[$org]['points'] = '';  // move points to the second column & set default value.
       }
       if ($answer['question'] != null) {
         $rec[$org][$answer['question']] = $answer['answer'];
       }
     }
     
     $csvFile = fopen(STARS_File::getFullFilesPath($this->exportFilename(),'CREDIT_EXPORT'), 'w');
     fputcsv($csvFile, array($this->getTitle(), ' ', 'Exported:',date("F j, Y, g:i a"))); 
     fputcsv($csvFile, $questions);  // TO DO: error handling
     foreach ($rec as $answerLine) {
       if (fputcsv($csvFile, $answerLine) === false) {
          die("Can't write CSV line");  // TO DO: improve error handling
       }
     }
     fclose($csvFile);

     return true;
  }


  // @TO DO: the functions are supplied as object and static method b/c
  //         Transaction Script code doesn't work with objects - that should change.
  /**
   * Build the form file name for this credit's PDF form.
   * @return string filename (NOT full path) for the PDF form for this credit.
   */
  public function formFilename()
  {
    $filename = $this->creditCode('_') . '.pdf';
    return $filename;
  }
  /**
   * Build the form file name for this credit's PDF form.
   * @return string filename (NOT full path) for the PDF form for this credit.
  */
  static public function getFormFilename($creditRecord)
  { 
    $filename = self::buildCreditCode($creditRecord,'_') . '.pdf';
    return $filename;
  }

  /**
   * Return a string that uniquely encodes this credit/category.
   * @param string seperator - character to use to seperate elements ('_'or ' ')
   * @return string that identifies this Credit (e.g., AF_Credit_06)
   *         or '' if the credit does not exist.
   */
  public function creditCode($seperator = '_')
  {
    return self::buildCreditCode( $this->getCreditInfo(), $seperator );
  }
  /**
   * Helper - form the credit code from a record of data.
   * @return string that identifies this Credit (e.g., AF_Credit_06)
   *         or '' if the credit does not exist.
   */
  static public function buildCreditCode($record, $seperator = '_')
  {
    if ($record['credittype'] == STARS_CREDIT_TT) {
      $creditNumber = $record['subsectionname'];
    }
    else {
      $creditNumber = $record['creditnumber']<10?'0':'';
      $creditNumber .= $record['creditnumber'];
    }
    $creditCode = $record['sectionabbr'] . $seperator .
        self::_getCreditTypeCode($record['credittype'], true) .
                  $seperator . $creditNumber;
    return $creditCode;
  }
  
  /**
   * Return a string that uniquely encodes the credit/category.
   * @return string that identifies this Credit (e.g., AF_Credit_06)
   *         or '' if the credit does not exist.
   */
  static public function getCreditCode($creditId)
  {
    $creditCode = '';
    try {
      $credit = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemvalue AS sectionabbr, di2.itemvalue as subsectionname
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         LEFT JOIN (dataitems AS di2)
         ON (c.dicreditsubcategory = di2.itemid)
         WHERE c.creditid = ?',
         array($creditId),
         Zend_Db::FETCH_ASSOC
      );

      if (count($credit) > 0) {
        $creditCode = self::buildCreditCode($credit[0]);
      }
    }

    catch(Zend_Db_Exception $e) { return '';}

    return $creditCode;
  }

  /**
   * Return a string that uniquely encodes this credit/category for PDF question.
   * Unfortunately, we didn't use the same encoding for questions in the PDF files...
   * @return string that identifies this Credit (e.g., AF-C6)
   *         or '' if the credit does not exist.
   */
  public function pdfQuestionCreditCode($seperator = '-')
  {
    return self::buildPdfQuestionCreditCode( $this->getCreditInfo(), $seperator );
  }
  /**
   * Helper - form the credit code from a record of data.
   * @return string that identifies this Credit (e.g., AF_C6)
   *         or '' if the credit does not exist.
   */
  static public function buildPdfQuestionCreditCode($record, $seperator = '-')
  {
    if ($record['credittype'] == STARS_CREDIT_TT) {
      $creditNumber = $record['dicreditsubcategory'];
    }
    else {
      $creditNumber = $record['creditnumber'];
    }
    $creditCode = $record['sectionabbr'] . $seperator .
                  self::_getCreditTypeCode($record['credittype']) . $creditNumber;
    return $creditCode;
  }
  
  /**
   * Helper: get code for the credit type
   *   Long codes: Credit, Prereq, T2
   *   Short codes: C, P, S
   */
  private function _getCreditTypeCode($creditType, $long=false)
  {
     switch ($creditType) {
       case STARS_CREDIT_CREDIT:
          return ($long ? 'Credit' : 'C');
          break;
       case STARS_CREDIT_PREREQ:
          return ($long ? 'Prereq' : 'P');
          break;
       case STARS_CREDIT_TT:
          return ($long ? 'T2' : 'S');  // S for sub-section
          break;
     }
     return ''; // default case - internal error - should NEVER happen!
  }
  
  /**
   * Helper: retrieve one record from the DB representing this Credit
   * @param integer $creditId POID for the record to retrieve
   * @return array containing the record, with DB fields as keys
   *         or null if DB operation failed.
   * @todo improve error handling.
   */
  private function _retrieveRecord($creditId)
  {
    try {
      $credit = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, 
        di2.itemdisplay AS subsectiontitle, di2.itemvalue as subsectionname
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         LEFT JOIN (dataitems AS di2)
         ON (c.dicreditsubcategory = di2.itemid)
         WHERE c.creditid = ?',
         array( $creditId),
         Zend_Db::FETCH_ASSOC
      );

      if (count($credit) > 0) {
        return $credit[0];
      }
      else {
        return null;
      }
    }

    catch(Zend_Db_Exception $e) { return null;}
  }

  /**
   * Fectch all the credits.
   * @return an array containing all credits (as STARS_Credit objects)
   *         or empty array if no credits exist.
   */
  static public function getAllCredits()
  {
    try {
      $creditRecs = Zend_Registry::get('db')->fetchAll
      (
        'SELECT c.*, di1.itemdisplay AS sectiontitle, di1.itemvalue AS sectionabbr, 
         di2.itemdisplay AS subsectiontitle, di2.itemvalue as subsectionname
         FROM credits AS c
         INNER JOIN (dataitems AS di1)
         ON (c.dicreditcategory = di1.itemid)
         LEFT JOIN (dataitems AS di2)
         ON (c.dicreditsubcategory = di2.itemid)',
         array(),
         Zend_Db::FETCH_ASSOC
      );

      // to do: this is O/R mapping layer stuff!
      $credits = array();
      foreach ($creditRecs as $rec) {
        $credit = new STARS_Credit($rec['creditid']);
        $credit->_record = $rec;
        $credits[] = $credit;
      }
      return $credits;
    }
    catch(Zend_Db_Exception $e) { return null;}
  }
  
  
  /**
   * Helper: retrieve all Answers submitted to questions for this credit.
   * @param integer $creditId POID for the record to retrieve
   * @return array containing the record, with DB fields as keys
   *         or null if DB operation failed.
   * @todo improve error handling.
   */
  private function _retrieveAnswers($creditId)
  {
    try {
      $answers = Zend_Registry::get('db')->fetchAll
      (
        'SELECT
           i.fullname AS orgname,  o.orgid, 
           Answers.question as question, Answers.answer as answer
         FROM organizations o
         LEFT JOIN (aashedata01.institutionnames i) 
         ON (o.nameid = i.id)
       
         LEFT JOIN (
           SELECT a.orgid AS orgid, q.questioncode AS question,  a.answer AS answer
           FROM dataquestions q
           LEFT JOIN dataanswers a
           ON q.questionid = a.dataquestionid

           WHERE q.creditid = ?
 
        UNION
           SELECT fa.orgid AS orgid, fq.questioncode AS question,  fa.answer AS answer
           FROM feedbackquestions fq
           LEFT JOIN feedbackanswers fa
           ON fq.questionid = fa.feedbackquestionid
           WHERE fq.creditid = ?
          UNION
           SELECT c.orgid AS orgid, "points" AS question,  c.pointsest AS answer
           FROM orgcreditfiles c
	         WHERE c.creditid = ?)
	        AS Answers
	       ON o.orgid = Answers.orgid
         ORDER BY orgname, question',
         array( $creditId, $creditId, $creditId),
         Zend_Db::FETCH_ASSOC
      );

      if (count($answers) > 0) {
        return $answers;
      }
      else {
        return null;
      }
    }

    catch(Zend_Db_Exception $e) { return null;}
  }
  
  /**
   * Helper: retrieve all Questions for this credit.
   *  IMPORTANT:  must sort results in same order as retrieveAnswers()
   * @param integer $creditId POID for the record to retrieve
   * @return array containing the record, with DB fields as keys
   *         or null if DB operation failed.
   * @todo improve error handling.
   */
  private function _retrieveQuestions($creditId)
  {
    try {
      $questions = Zend_Registry::get('db')->fetchAll
      (
        'SELECT questioncode
         FROM dataquestions 
				 WHERE creditid = ?
				UNION

				SELECT questioncode
         FROM feedbackquestions 
				 WHERE creditid = ?
				ORDER BY
						questioncode',
         array( $creditId, $creditId),
         Zend_Db::FETCH_COLUMN
      );

      if (count($questions) > 0) {
        return $questions;
      }
      else {
        return null;
      }
    }
    catch(Zend_Db_Exception $e) { return null;}
  }

}
