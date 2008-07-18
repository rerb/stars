<?php
/**
 * STARS_CreditPdfFile
 * 
 * Responsible for hiding implementation of a Credit PDF file.
 *   Provides methods to store and retreive PDF file objects.
 *
 * @author J. Fall
 * @version 0.1
 * @package stars.application
 * @subpackage model
 * @todo Add error handling
 * Note:  This class serves two functions - it is a domain object and a DB mapper
 */
class STARS_CreditPdfFile extends STARS_File
{
  const TABLE = 'orgcreditfiles';  // the DB table for credit files
  const KEY = 'orgcreditfileid';   // primary key for the table.

  /**
   * Construct a new CreditPdfFile from the PDO.
   * @param integer $orgCreditFileId the POID for the file to load, or
   *                 null to create a new File, where !isValidFile().
   */
  public function __construct($orgCreditFileId=null)
  {
    parent::__construct(self::TABLE, self::KEY, $orgCreditFileId);
  }
    
  /**
   * Factory method: attempt to load a CreditPdfFile for the given org-credit.
   * @param integer $creditOID POID for associated credit.
   * @param integer $orgOID POID for associated organization.
   * @return CreditPdfFile the associated File, or null if it doesn't exist.
   */
  static public function getCreditPdfFile($creditOID, $orgOID)
  {
    $fileObj = null;
    $key = self::_fetchKey($creditOID, $orgOID);

    if ($key) 
    {
      $fileObj = new STARS_CreditPdfFile($key);
    }
    return $fileObj;
  }

  /**
   * Factory method: create a new CreditPdfFile for a freshly uploaded file.
   * @param $fileInfo  $_FILES array for uploaded file
   * @param integer $creditOID POID for associated credit.
   * @param integer $orgOID POID for associated organization.
   * @param $points estimated points for this submission.
   * @return new CreditPdfFile object or null if it could not be created.
   * @todo: error handling - encode path and upload could fail!
   */
  static public function upload($fileInfo, $creditOID, $orgOID, $points)
  {
    $filepath = self::_encodeFilePath($creditOID, $orgOID);  // TO DO: error check!
    $record = array(
          'creditid'     => $creditOID,
          'orgid'        => $orgOID,
          'modifierid'   => STARS_Person::getInstance()->get('personid'),
          'status'       => 1,
          'pointsest'    => $points,
          'filepath'     => $filepath,
    );

    // Update vs. Insert?
    if ( ! ($fileObj = self::getCreditPdfFile($creditOID, $orgOID) ) )
    {
      $fileObj = new STARS_CreditPdfFile();
    }  
    return parent::upload($fileObj, $fileInfo, $record);  
  } 

  // Add methods here to assist validating the file based on the
  // credit it is supposed to be attached to.

  /**
   * Get information about one credit form
   * @param STARS_Credit $credit - the credit record to retieve info about.
   * @return array of information about the credit form ('available', 'filename', 'link')
   * @to do:  this should really work on credit objects!
   */
  static public function getFormInfo($credit)
  {
    $info = array();
    //$formFilename = $credit->getFormFilename();
    $formFilename = STARS_Credit::getFormFilename($credit);
    $formFilepath = STARS_File::getFullFilesPath($formFilename, 'CREDIT_FORM');
    if (file_exists($formFilepath)) {
      $info['available'] = true;
      $info['filename'] = $formFilename;
      $info['link'] = '/credit/downloadform/form/'.$formFilename;
    }
    else {
      $info['available'] = false;
    }
    return $info;
  }
  
  /**
   * Get information about one previously submitted credit file
   * @param STARS_Credit $credit - the credit record to retieve info about.
   * @return array of information about the creditfile ('exists', 'filename', 'link')
   * @to do:  this should really work on credit objects!
   */
  static public function getSubmissionInfo($credit)
  {
    $info = array();
    if (! empty($credit['status'])) {
      $file = new STARS_CreditPdfFile($credit['orgcreditfileid']);
      // @todo: error handling - if file doesn't exist, DB is inconsistent with filesystem.
      $info['available'] = true;
      $info['filename'] = $file->getDisplayName();
      $info['link'] = '/credit/savefile/' . $credit['creditid'];
    }
    else {
      $info['available'] = false;
    }
    return $info;
  }
  
  /**
   * Get information about submitting credit file
   * @param STARS_Credit $credit - the credit record to retieve info about.
   * @return array of information about submitting ('code','uploadLink', 'uploadTitle')
   * @to do:  this should really work on credit objects!
   */
  static public function getSubmitInfo($credit)
  {
    $info = array();
    $creditCode = STARS_Credit::buildCreditCode($credit, ' ');
    $info['creditCode'] = $creditCode;
    $info['uploadLink'] = '/credit/upload/'.$credit['creditid'];
    $uploadTitle = (empty($credit['status']) ?'Submit Data':'View / Edit your submission');
    $info['uploadTitle'] = $uploadTitle . ' for ' . $creditCode;
    return $info;
  }

  /**
   * Get the Persistent Object ID of the credit associated with this file.
   * @return integer credit POID for this CreditPdfFile (null if !persists())
   */
   public function getCreditId()
   {
     $info = $this->getFileInfo();
     return $info['creditid'];
   }
   
  /**
   * Get the estimated points associated with this file.
   * @return string points for this CreditPdfFile (null if !isValidFile())
   */
   public function getPoints()
   {
     $info = $this->getFileInfo();
     return $info['pointsest'];
   }

  /**
   * Helper: Attempt to fetch the TABLE KEY for the given org-credit.
   * @param integer $creditOID POID for associated credit.
   * @param integer $orgOID POID for associated organization.
   * @return DB record for the given credit and organization, or null.
   * @todo: add exception handling for DB query
   */
  static protected function _fetchKey($creditOID, $orgOID)
  {
    try
    {
      $record = Zend_Registry::get('db')->fetchOne
      (
        "SELECT " . self::KEY .
        " FROM " . self::TABLE .
        " WHERE creditid = ? AND orgid = ?",
        array( $creditOID, $orgOID),
        Zend_Db::FETCH_ASSOC
      );

      return $record;
    }
    catch(Zend_Db_Exception $e) 
    { 
      return null;  // Not good!  Need proper exception handling here!!!!
    }
  }

  /**
   * Helper: Encode a unique relative file path for this file.
   * @param $creditOID  POID for credit to encode path for.
   * @param $orgOID  POID for the organization storing this credit.
   * @return string - unique path for the file for this org/credit,
   *         or '' if the credit does not exist.
   *   Side-effect: Ensure the directory for this file exists.
   * @todo: need some error checking here on credit, org, filesystem op!!!
   */
  private static function _encodeFilePath($creditOID, $orgOID)
  {
    $creditCode = STARS_Credit::getCreditCode($creditOID);
    $filename = $creditCode . '_Org' . $orgOID . '.pdf';
    parent::createFilesDir($creditCode);  // To Do: handle filesystem error.
    $filepath = $creditCode . '/'. $filename;
    return $filepath;
  }
}
