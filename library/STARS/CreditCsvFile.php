<?php
/**
 * STARS_CreditCsvFile
 * 
 * Responsible for hiding algorithms for importing data from a Credit CSV file.
 *   Provides methods to import CSV files created from merged PDF credit forms.
 *   Includes loads of validation to ensure data looks valid before importing.
 *
 * @author J. Fall
 * @version 0.1
 * @package stars.application
 * @subpackage model
 */
class STARS_CreditCsvFile
{
  protected $_userid;     // the user that is performing operations on this CSV file
  protected $_credit;     // the credit this CSV file ostensibly contains data for
  protected $_creditCode; // code (e.g., AF_Credit_01 ) for the credit
  protected $_filename;   // the name of the CSV file for the credit
  protected $_path;       // full path to the file.
  protected $_errorMsg;   // Error message generated on import.
  
  /**
   * Construct the CreditCsvFile for the given credit
   * @param STARS_Credit $credit the credit object to get CSV file for.
   */
  public function __construct($credit)
  {
    // assert: $credit != null
    $this->_userid = STARS_User::getId();
    $this->_credit = $credit;
    $this->_creditCode = $credit->creditCode();
    $this->_filename = $credit->csvFilename();
    $this->_path = STARS_File::getFullFilesPath( $this->_filename, 'CREDIT_DATA');
    $this->_errorMsg = array();
  }
    
  /**
   * Attempt to import data from the file.
   *   Side-effect: call getImportError() to get error message if false is returned.
   * @return boolean true if file successfully imported, false otherwise.
   */
  public function import()
  {
    // Open the file and check the header line
    if ( ($fp = $this->_open()) == NULL ||
         ($questions = $this->_loadHeader($fp )) == NULL ) {
      return false;
    }
    // Ensure all the questions in this file exist in the DB.
    $this->_updateQuestions($questions);
    
    // If we get here, things look good - import the rest of the data:
    // First load all the records from the CSV file
    //  then do a bulk INSERT / UPDATE to store them in the DB.
    $answers = array();  // actually a 2-D array, one array of answers per org.
    $numQuestions = count($questions);
    while ($answers[] = $this->_loadRecord($fp, $numQuestions)) {
      ;
    }
    array_pop($answers); // loop above puts null record in last element of answers array
    $this->_saveAnswers($questions, $answers);

    fclose($fp);
    return ! $this->hasErrors();
  }
  
  /**
   * Helper: Save a set of answers to the database.
   *    ASSUMES: - no DB table uses answerid as a foriegn key
   *             - quesionid-orgid is a UNIQUE KEY in answer tables.
   * @param $questions  array of question objects loaded from CSV file header.
   * @param $answers    corresponding array of answers for each organization
   */
  private function _saveAnswers($questions, $answers)
  {
    $db = Zend_Registry::get('db');
    // IMPORTANT: assumes that questionid-orgid is a UNIQUE KEY in DB
    $questionType = array('feedback'=>true, 'data'=>false);
    foreach ($questionType as $prefix=>$isFeedback) {  // for each question type table
      $table = $prefix . 'answers';
      $qid   = $prefix . 'questionid';
      $keys = "(orgid, $qid, answer, modifierid)";
      $values = '';
      $n = count($questions);
      foreach ($answers as $orgAnswers) {
        $orgid = $orgAnswers['orgid'];
        for ($i=0; $i<$n; $i++) {
          if ($questions[$i]->isFeedback == $isFeedback) {  // match questions type
            $questionid = $questions[$i]->questionid;
            $answer = $db->quote($orgAnswers[$i]);
            if (strlen($values) > 0) $values .=',';
            $values .= "('$orgid','$questionid',$answer,'{$this->_userid}')";
          }
        }
      }
      // Simple bulk replace all the answers for this credit.
      // IMPORTANT: assumes UNIQUE KEY in table 
      //            AND no others refer to tabel in foreign key.
      if (strlen($values)>0) {
        $sql = "REPLACE INTO $table $keys VALUES $values";
        $stmt = new Zend_Db_Statement_Mysqli($db, $sql);
        $stmt->execute();
      }
    }
  }

  /**
   * Helper: ensure that all questions exist in the database & get their IDs.
   * @param $questions  array of question objects loaded from CSV file header.
   *     Side-Effect - modified to add questionid field to each record.
   * @throws fatal error if internal or DB inconsistency is identified.
   */
  private function _updateQuestions(&$questions)
  {
    // Several algorithms are possible here with different efficiency per situation.
    // This one assumes that the questions are largely fixed, and will be added once,
    //  the first time they are encounted, and otherwise we primarily want to
    //  efficiently get the DB id's for existing questions.
    
      // First: Attempt to simply get the ID's for existing quesions
      //        AND identify any questions that were missing from the DB.
      // This avoids calling INSERT when all the questions already exist.
      $missing = $this->_getQids($questions);

      if (count($missing) > 0) { // Some questions need to be added to DB
        $this->_insertQuestions($questions);
      
        // Now attempt to get the ID's for the added quesions
        $missing = $this->_getQids($questions, $missing);
        
        // Check for internal consistency - all questions should be loaded now,
        //  if not, serious error with algorithm - abort.
        if (count($missing)>0) {
          throw new STARS_Exception('Credit ' . $this->creditCode . 
                                    ' : Unable to add questions ['.
                                    implode(',', $mising) . ']'); 
        }
      }
  }

  /**
   * Helper: INSERT all questions to the DB (ignoring those that already exist).
   *   ASSUMES: questioncode is a UNIQUE KEY in answer tables
   * @param $questions objects with info about questions, 
   *                  including its unique question-code (e.g., AF-C1-Q2 ).
   */
  private function _insertQuestions($questions)
  {
    // Can't use 'missing' results of SELECT above b/c could be RACE condition,
    //  instead, use ON DUPLICATE KEY UPDATE clause to ignore any existing question.
    // Usually add all questions for a credit at once in any case, so don't get fancy.
    // IMPORTANT: assumes that questioncode is a UNIQUE KEY in DB
    $creditId = $this->_credit->getId();
    $tables = array('feedbackquestions'=>true, 'dataquestions'=>false);
    $keys = '(creditid, questioncode, question, diquestiontype, displayorder)';
                                             // question type 24 == text area
    foreach ($tables as $table=>$isFeedback) {  // for each question type table
      $values = '';
      foreach ($questions as $question) {
        if ($question->isFeedback == $isFeedback) {   // match questions type
          if (strlen($values) > 0) $values .=',';
          $values .= "('$creditId','{$question->code}','{$question->code}',24,'{$question->number}')";
        }
      }
      // Attempt to do the insert, if questioncode is a duplicate, just ignore
      // @todo Search for Mysqli references, change to $db->query() form.
      $sql = "INSERT INTO $table $keys VALUES $values "  .
             "       ON DUPLICATE KEY UPDATE questionid=LAST_INSERT_ID(questionid)";
      $stmt = new Zend_Db_Statement_Mysqli(Zend_Registry::get('db'), $sql);
      $stmt->execute();
    }
  }

  /**
   * Helper: Query DB to get ID's for each question, if possible.
   * @param $questions  array of question objects loaded from CSV file header.
   *     Side-Effect - modified to add questionid field to each record.
   * @param $indicies  arrary [qcode=>index] of indexes to update, or NULL to do all
   * @return  array of indexes for questions that did not exits in DB
   */
  private function _getQids(&$questions, $indicies = NULL)
  {
      // build the indicies array,if we didn't get one
      if ($indicies == NULL) {
        $indicies = array();
        $n = count($questions);
        for ($i=0; $i<$n; $i++) {
          $indicies[$questions[$i]->code] = $i;
        }
      }

      // Attempt to retreive the question records for the given credit
      $creditId = $this->_credit->getId();
      $qRecords = Zend_Registry::get('db')->fetchAll
      (
        "(SELECT questionid, questioncode, creditid
         FROM dataquestions
         WHERE creditid = ?)
         UNION
         (SELECT questionid, questioncode, creditid
         FROM feedbackquestions
         WHERE creditid = ?)",
         array($creditId, $creditId),
         Zend_Db::FETCH_ASSOC
      );
      // add any questionid fields we found to the question record
      //  AND remove any index we find to indicate that it was found.
      foreach ($qRecords as $rec) {
        $code = $rec['questioncode'];
        if (isset($indicies[$code])) {
          $questions[ $indicies[$code] ]->questionid = $rec['questionid'];
          unset($indicies[$code]);
        }
      }
      // return indicies for any questions not located in the DB.
      return $indicies;
  }


  /**
   * Helper: load and check validity of one row of data in the CSV file.
   * @param $fp  file pointer for this file.
   *   PRE: $fp is at first character in data line (2nd or greater) in file.
   * @param: $numQ integer  number of questions we're expecting answers for.
   * @return array of answers if row is valid for this credit, NULL otherwise.
   */
  private function _loadRecord($fp, $numQ)
  {
    if (! ($answers = fgetcsv($fp)) ) {  // End of File
      return NULL;
    }
    if (count($answers) != $numQ+1) {
      $this->_logError('Invalid record [' .$answers[0].'] (expecting '.$numQ.' answers) in CSV file ' . $this->_filename);
      return NULL;
    }
    // The first answer is the PDF file name with the encoded Orgid - AF_C1_Org1.pdf   or  AF_T2_Buildings_Org1.pdf
    //   Get the plain Org ID and the credit code
    $start = strpos($answers[0], 'Org');
    $orgid = substr($answers[0], $start+3, -4);
    $code = substr($answers[0], 0, $start-1);
    
    // Verify that the merged PDF file belongs to the correct credit
    if ( $start == null ) {
      $this->_logError('Invalid record ['.$answers[0].'] does not have valid form [CC_Credit_Org#.pdf] in file ' . $this->_filename);
      return NULL;
    }
    else if ($code != $this->_creditCode ) {
      $this->_logError('Invalid record ['.$answers[0].'] does not match credit ['.$this->_creditCode.'] in file ' . $this->_filename);
      return NULL;
    }
    array_shift($answers);
    $answers['orgid'] = $orgid;
    return $answers;
  }
  
  /**
   * Helper: load and check validity of header.
   * @param $fp  file pointer for this file.
   *   PRE: $fp is at first character in open file.
   * @return array of question identifiers if header is valid for this credit, NULL otherwise.
   */
  private function _loadHeader($fp)
  {
    if ((! ($header = fgetcsv($fp))) ||
        count($header) < 2 ) {
      $this->_logError('File ' . $this->_path . ' is not a valid CSV file.');
      return NULL;
    }
    array_shift($header); // first column is pdf filenames - no header.
    // Subsequent columns are Question ID's, which should match the credit info.
    $questions = array();
    $creditCode = $this->_credit->pdfQuestionCreditCode();
    foreach ($header as $field) {
      // Field Format:  form1[0].AF-C1-Q2[0]  (annoying!  Adobe!)
      $qCode = substr($field, 9, -3);  // NOTE: may need more elaborate algorithm here!
      $parts = explode('-', $qCode);
      if (count($parts) < 3 || $creditCode != $parts[0].'-'.$parts[1]) {
        $this->_logError('CSV header ['.$qCode.'] does not match credit ['.$creditCode.'] in file ' . $this->_filename);
        return NULL;
      }
      $q = new stdClass;
      $q->isFeedback = strtolower(substr($parts[2],0,1))=='f';
      $q->code = $qCode;
      $q->number = substr($parts[count($parts)-1], 1);
      $questions[] = $q;
    }
    
    return $questions;
  }
  
  /**
   * Helper: attempt to open the file for reading.
   * @return file pointer if file opened successfully, NULL otherwise.
   */
  private function _open()
  {
    if (! file_exists( $this->_path ) ) {
      $this->_logError('File ' . $this->_path . ' does not exist.');
      return NULL;
    }
    if (! ($fp = fopen($this->_path, 'r')) ) {
      $this->_logError('File ' . $this->_path . ' could not be opened.');
      return NULL;
    }
    return $fp;
  }

  /**
   * Get the filename for this File.
   * @return string filename of this File.
   */
  public function getFileName()
  {
    return $this->_filename;
  }

  /**
   * Does the file exist on the filesystem?
   * @return boolean true if the file exists, false otherwise.
   */
  public function fileExists()
  {
    return file_exists( $this->_path );
  }

  /**
   * Get any error message generated while attempting to import() this File.
   * @return array of strings with error text, or empty array if no error was generated.
   */
  public function getImportErrors()
  {
    return $this->_errorMsg;
  }
  
  /**
   * Does this file have any errors associated with it?.
   * @return true if the there were errors generated during the import, false otherwise.
   */
  private function hasErrors()
  {
    return count($this->_errorMsg) > 0;
  }

  /**
   * Helper: log an error message.
   * @param $msg the error message to log.
   */
  private function _logError($msg)
  {
    $this->_errorMsg[] = $msg;
  }
}
