<?php
/**
 * STARS/File.php
 *
 * Abstract base class for File object
 * Provides access to a file FILE_PATH in the FILES_ROOT directory,
 *  with the user-provided-name DISPLAY_NAME
 * 
 * @author J. Fall 
 * @version 0.1
 * @package STARS
 */
define ("FILES_ROOT",$_SERVER['DOCUMENT_ROOT'].'/../files');
define ("DISPLAY_NAME", 'userfilename');  // field with user's file name
define ("FILE_PATH", 'filepath');  // field with path to file on server

/**
 * STARS_File
 * A File provides access to items referenced from a DB field,
 *   but maintained in a filesystem.
 * A File hides the DB queries and filesystem access required 
 *  to store and reteive  files.
 * A File is responsible for maintaining the data integrity between the
 *  filesystem item and the associated row in the DB.
 * 
 * Sub-class must supply two filename fields, defined above.
 *
 * @package STARS
 * @subpackage model
 */
abstract class STARS_File
{
  /**#@+
   * Define error flags for the {@link _write()} operation.
   */
  const SUCCESS = 1;
  const OTHER_ERROR = -1;

  //  DANGER - the _record and _fileOID fields are not always set.
  //  Sub-classes should not reference these directly - use accessors.
  protected $_record;   // associative array containing file row
  protected $_fileOID;  // POID for this file object or null for new files
  protected $_table;    // table name in DB where file records are stored
  protected $_key;      // primary key field for DB table

  /**
   * Construct a new File object for the given PDO.
   * @param string $table DB table where file records are stored
   * @param string $keyField key for above table
   * @param integer $fileId the POID for the file to load, or
   *                 null to create a new File, where !isValidFile().
   */
  protected function __construct($table, $keyField, $fileId=null)
  {
    $this->_table = $table;
    $this->_key = $keyField;
    $this->_clearRecord();  // using lazy read
    $this->_fileOID = intval($fileId);
  }
  
  /**
   * Handle a freshly uploaded file.
   * @param File $fileObj  File to load freshly uploaded file for.
   * @param $fileInfo  $_FILES array for uploaded file
   * @param array $record  DB record describing the uploaded file,
   *          must define at least the FILE_PATH 
   * @return copy of $fileObj with correct DISPLAY_NAME set or 
   *             null if file could not be uploaded or record saved.
   *    Side effects: record written to DB
   *                  file stored in FILES_ROOT
   * @todo improve error handling logic.
   */
  static public function upload($fileObj, $fileInfo, $record)
  {
    $status = self::OTHER_ERROR;
    $filepath = $record[FILE_PATH];
    $fullpath = self::getFullFilesPath($filepath);
    
    if ( move_uploaded_file($fileInfo['tmp_name'], $fullpath) ) 
    {
      $fileObj->_record = $record;
      $fileObj->_record[DISPLAY_NAME] = $fileInfo['name'];

      // Minor data integrity issue here if write fails after move file succeeds - especially for upadtes.
      $status = $fileObj->_write();
    }
    if ($status == self::SUCCESS)
      return $fileObj;
    else
      return null;
  } 

  /**
   * Has the DB record for this File been specified?
   * @return boolean true if this File has its DB record defined, false otherwise.
   */
  public function isValidFile()
  {
    $record = $this->getFileInfo();

    return ( count($record) > 0 );
  }

  /**
   * Remove this file from both the DB and the filesystem.
   * Responsible for maintaining data integrity b/w filesystem & DB
   * @return boolean true if the file was removed, false if it could not be.
   * @todo  error handling logic should provide some reason why delete failed.
   */
  public function delete()
  {
    // Opportunity for messed up data integrity is high here because
    // if either file or record delete fails, things are out of sync.
    // Strategy: remove record, then remove file
    //           if file remove fails & file exists, restore record.
    $path = $this->getFullPath();
    $removed = $this->_removeRecord();
    if ($removed)
    {
      if ( file_exists( $path ) && 
           (! $removed = unlink($path)) )
      {
        // OOPS - file was not removed - restore record.
        $this->_write();
      }
      else
      {
        $this->_clearRecord();  // all is well - clear all traces.
      }
   }
   return $removed;
  }

  /**
   * Get the user's filename for this File.
   * PRE: isValidFile()
   * @return string filename to display to user to represent this File.
   */
  public function getDisplayName()
  {
    $record = $this->getFileInfo();
    return $record[DISPLAY_NAME];
  }
  
  /**
   * Does this File persist in the DB yet?
   * @return boolean true if the File has a POID, false otherwise.
   */
  public function persists()
  {
    return$this->_fileOID != null;
  }

  /**
   * Get the Perstent Object ID for this File.
   * @return integer POID for this File, or null is !persists()
   */
  public function getId()
  {
    return $this->_fileOID;
  }

  /**
   * Does the file exist on the filesystem yet?
   * @return boolean true if the file exists, false otherwise.
   */
  public function fileExists()
  {
    return file_exists( $this->getFullPath() );
  }

  /**
   * Get the absolute filesystem path for this File.
   * PRE: isValidFile()
   * @return string abs. filesystem path to file maintained by this File.
   */
  public function getFullPath()
  {
    $record = $this->getFileInfo();
    return self::getFullFilesPath($this->_record[FILE_PATH]);
  }

  /**
   * Get the absolute filesystem path to a path relative to files directory.
   * @param string $filepath  a relative filesystem path
   * @return string abs. filesystem path to $filepath in files directory.
   */
  protected static function getFullFilesPath($filepath)
  {
    return realpath(FILES_ROOT) .'/'. $filepath;
  }

  /**
   * Get the database record for this File
   * @return array where keys are DB fields, or empty array if !persists()
   */
  public function getFileInfo()
  {
    // Lazy read - load here if file info not loaded yet.
    if ($this->_record == null && $this->_fileOID)
    {
      $this->_record = $this->_retrieveRecord($this->_fileOID);
    }

    if ( $this->isValidRecord($this->_record) )
    {
      return $this->_record;
    }
    else
    {
      return array();
    }
  }
  
  /**
   * Helper:does the DB record passed in describe this File object?
   * @return boolean true if the record is valid, false otherwise.
   */
  private function isValidRecord($record)
  {
    return (is_array($record)  && 
            $record[$this->_key] == $this->_fileOID );
  }

  /**
   * Ensures the sub-directory below the files directory exists.
   * @param $dir the path to create within files
   * @return true if the directory exists, false if it could not be created.
   * @throws Exception if the directory cannot be created.
   */
  static public function createFilesDir($dir)
  {
    $dirpath = self::getFullFilesPath($dir);
    if (!is_dir($dirpath)) 
    {
      mkdir($dirpath,0700);
    }
    return file_exists($dirpath);
  }

  /**
   * Store array of attributes for this file in the database.
   * Data Integrity: Assumes actual file is successfully stored already.
   * Assumes all fields to be written are loaded in $this->_record.
   * @return SUCCESS if record written, OTHER_ERROr if not.
   *   Side Effect: sets KEY field for this object to POID
   */
  protected function _write()
  {
    try
    {
      if ($this->persists())
      {
        Zend_Registry::get('db')->update($this->_table, $this->_record, $this->_key . '= ' . $this->_fileOID);
      }
      else
      {
        Zend_Registry::get('db')->insert($this->_table, $this->_record);
        $this->_fileOID = 
          $this->_record[$this->_key] =Zend_Registry::get('db')->lastInsertId();
      }
      return self::SUCCESS;
    }

    catch(Zend_Db_Statement_Mysqli_Exception $e)
    {
      return self::OTHER_ERROR;
    }
  }

  /**
   * Helper: removes record from the DB, but does not clear private data.
   * Caller should also call _clearRecord() after this call to maintain
   *  correct data integrity.
   * @return number of items removed from database (0 for not successful)
   */
  private function _removeRecord()
  {
    $db = Zend_Registry::get('db');
    $n = $db->delete( $this->_table, 
             $this->_key ." = " . $db->quote($this->_fileOID, 'INTEGER') );
    if ($n)
      $this->_fileOID = null;  // this is no longer valid, no matter what.
    return $n;
  }

  /**
   * Helper: clear the private members storing data for this file object.
   * Essentially, turns this object into a new, empty File.
   */
  private function _clearRecord() 
  {
    $this->_record = null;
    $this->_fileOID = 0;
  }

  /**
   * Helper: retrieve one record from the $_table
   * @param integer $fileId POID for the record to retrieve
   * @return array containing the record, with DB fields as keys
   *         or null if DB operation failed.
   * @todo improve error handling.
   */
  private function _retrieveRecord($fileId)
  {
    try
    {
      $record = Zend_Registry::get('db')->fetchAll(
                "SELECT f.*
                FROM $this->_table AS f
                WHERE f.$this->_key = ?",
                array( $fileId),
                Zend_Db::FETCH_ASSOC
      );
      if (count($record) > 0)
      {
        return $record[0];
      }
      else
      {
        return null;
      }
    }

    catch(Zend_Db_Exception $e) { return null;}
  }
}
