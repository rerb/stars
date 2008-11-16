<?php
/**
 * application/contollers/CreditController.php
 *
 * Actions for Credit manipulation
 * 
 * @author J. Fall 
 * @version 0.1
 * @package STARS
 */

/**
 * CreditController: A {@link STARS_ActionController} with actions:
 *  /credit/index            - not sure what this should do?? Any ideas?
 *  /credit/upload/credit=#  - Upload a Credit PDF file for credit #
 *  /credit/viewfile/?id=#   - Serve Credit PDF file # to browser
 *  /credit/savefile/?id=#   - Serve Credit PDF file # for save
 *  /credit/getfile/?fid=#   - Serve Credit PDF file (direct access)
 *  /credit/deletefile/?id=# - Delete Credit PDF file #
 *  /credit/import           - Import credit data from merged PDF data (CVS file)
 *  /credit/export           - Export credit answers from DB to CSV files
 *
 * @package STARS
 * @subpackage controllers
 */
class CreditController extends STARS_ActionController
{
  /**
   * /credit/export
   * Export credit data from DB to CSV files.
   */
  public function exportAction()
  {
    // This is an admin function
    $this->_protect(2);
    set_time_limit(0); // This might take a while - don't let the script time-out...
                       // This could be bad if the script has an infinite loop!
    $form = new STARS_Form(new Zend_Config_Ini('../config/exportcredits.ini', 'config'));
       
    if ($this->_request->isPost() &&
        $form->isValid($this->_request->getPost()) )
    {
      $this->view->report = $this->_doExport();
    }
    else { // show form ONLY for GET requests
       $this->view->form = $form->render(new Zend_View);
    }
  }

  /**
   * Helper: perform Credit Data export to CSV files
   * @return report object with $errorList and $exportList array elements
   */
  private function _doExport()
  {
    $report = new stdClass();
    $report->exportList = array();
    $report->errorList = array();
    
    $credits = STARS_Credit::getAllCredits();
//    foreach ($credits as $credit) {
$credit = new STARS_credit(79);
      if ($credit->export()) {
        $report->exportList[] = $credit->exportFilename();
      }
      else {
        $report->errorList[$credit->exportFilename()] = $credit->getExportErrors();
      }
//    }

    return $report;
  }


  /**
   * /credit/import
   * Import any credit data from CSV files merged from PDF credit forms.
   */
  public function importAction()
  {
    // This is an admin function
    $this->_protect(2);
    set_time_limit(0); // This might take a while - don't let the script time-out...
                       // This could be bad if the script has an infinite loop!
    $form = new STARS_Form(new Zend_Config_Ini('../config/importcredits.ini', 'config'));
       
    if ($this->_request->isPost() &&
        $form->isValid($this->_request->getPost()) )
    {
      $this->view->report = $this->_doImport();
    }
    else { // show form ONLY for GET requests
       $this->view->fileList = $this->_getCsvFiles();
       
       $this->view->form = $form->render(new Zend_View);
    }
  }
  
  /**
   * Helper: identify all existing merged PDF CSV files to be imported
   * @return array of STARS_CreditCsvFile objects to import.
   */
  private function _getCsvFiles()
  {
    $files = array();
    $credits = STARS_Credit::getAllCredits();
    foreach ($credits as $credit) {
      $file = new STARS_CreditCsvFile($credit);
      if ($file->fileExists()) {
        $files[] = $file;
      }
    }
    return $files;
  }

  /**
   * Helper: perform Credit Data import from merged PDF CSV files
   * @return report object with $errorList and $importList array elements
   */
  private function _doImport()
  {
    $report = new stdClass();
    $report->importList = array();
    $report->errorList = array();
    
    $files = $this->_getCsvFiles();
    foreach ($files as $file) {
      if ($file->import()) {
        $report->importList[] = $file->getFileName();
      }
      else {
        $report->errorList[$file->getFileName()] = $file->getImportErrors();
      }
    }

    return $report;
  }

  /**
   * /credit/formsdownload/?form=filename
   * Attempt to retrieve the given file for download.
   * @param form filename is the name of the file to server
   * @todo Move action to generic FileController
   */
  public function downloadformAction()
  {
    //Form downloads are not available to the public
    $this->_protect(1);

    $filename = $this->_getParam('form');
    $this->view->filepath = STARS_File::getFullFilesPath($filename, 'CREDIT_FORM');
    if (! file_exists($this->view->filepath)) 
    {
       throw new STARS_Exception('Invalid Filename');
    }
    $this->view->filename = $filename;
    $this->_helper->layout->disableLayout(); // no layout for PDF views
   // just re-use the savefile view here
    $this->view->script = 
         '../application/views/scripts/credit/savefile.phtml';
  }

  /**
   * /credit/upload/?credit=#
   * GET:  present file UploadForm to upload a PDF Credit file
   * POST: attempt to upload the user's file
   * @param integer id is the POID of Credit to upload file for
   * @todo error handling
   */
  public function uploadAction()
  {
    $helper = new CreditFileActionHelper($this);
    $credit = $helper->_credit;
    $creditFile = $helper->_creditFile;
    
    $helper->initView('Submission');
    $helper->addViewFileOptions();
    $this->view->error = false;

    $formOptions = $helper->getLegendLabel();
    $formOptions['pointsOptions'] = false;
    $pointsAvail = $credit->getPointsAvailable();
    if (!$credit->isPrereq() && $pointsAvail>0) {  // pre-req's don't have points
      $pointsOptions = array('please select...', 'not applicable');
      for ($i=0; $i<=$pointsAvail; $i++) {
        $pointsOptions[] = $i;
      }
      $formOptions['pointsOptions'] = $pointsOptions;
    }
    if ($credit->isTier2()) {
      $formOptions['pointsLabel'] = 'Number of Tier Two credits claimed';
    }
    else {
      $formOptions['pointsLabel'] = 'Estimated points for this credit';
    }
    $form = new forms_UploadForm( $formOptions );
    $this->_populateUploadForm($form, $creditFile, $formOptions['pointsOptions']);

    if ($this->_request->isPost()) 
    {
      $formData = $this->_request->getPost();
      $formData['STARS_credit'] = $credit; // validation context.
      if ($form->isValid($formData) &&
          $creditFile = $this->_storeData($form->getValues(), $credit, 
                                          $formOptions['pointsOptions']) )
      { // DONE!  re-direct back to section dashboard
        $this->_flashMessage('File '.$creditFile->getDisplayName() .' was successfully uploaded for '.$credit->getTitle());
        $this->_redirect('/section/'. $credit->getSectionId() );
      } 
      else // either the form was invalid or there was an error storing the file
      {    // TO DO: better error handling?
        $this->view->error =true;
        $form->populate($formData);
      }
    }
    // show upload form for both GET and POST
    $this->view->form = $form;
  }

  /**
   * Helper: store post data and save the file itself.
   */
  private function _storeData($data, $credit, $pointsOptions)
  {
    $orgId = STARS_Person::getInstance()->get('orgid');
    // Convert the index from points options to the actual number of points.
    if ($pointsOptions) {
      $points = issetor($pointsOptions[$data['points']], 0);
    }
    else {
      $points = $data['points'];
    }
    $file = STARS_CreditPdfFile::upload($data['file'], $credit->getId(), $orgId, $points);
    return $file;
  }
  
  /**
   * Helper: re-populate upload form from creditPdfFile data
   */
  private function _populateUploadForm($form, $creditPdfFile, $pointsOptions)
  {
    if ($creditPdfFile)
    {
      // convert actual points back to an index in the points options
      $pointsIndex = 0;
      $points = $creditPdfFile->getPoints();
      if ($pointsOptions) {
        $pointsIndex = array_search($points, $pointsOptions);
        if ($pointsIndex === false)
          $pointsIndex = 0;
      }
      $data = array(
        'points' => $pointsIndex,
      );
      $form->populate($data);
    }
  }

  /**
   * /credit/confirmdelete/?credit=#
   * This action should probably move to a fileController in future?
   * This action passes a session token to the delete confirmation 
   * so it can validate the delete transaction.
   * @param integer credit is the POID of Credit to delete file for
   */
  function confirmdeleteAction()
  {
    $helper = new CreditFileActionHelper($this);
    $helper->confirmFileExists();
    $credit = $helper->_credit;
    $creditId = $credit->getId();
    $creditFile = $helper->_creditFile;
    
    $this->_storeToken( $creditFile->getId() );

    $helper->initView('Delete Submission');
    $helper->addViewFileOptions();
    $this->view->deleteAction = "/credit/deletefile/?credit=$creditId";
    $this->view->cancelAction = "/credit/upload/?credit=$creditId";
  }

  /**
   * /credit/deletefile/?credit=#
   * This action should probably move to a fileController in future?
   * This action expects a session token from the delete confirmation 
   * to validate the delete  transaction.
   * @param integer credit is the POID of Credit to delete file for
   */
  function deletefileAction()
  {
    $helper = new CreditFileActionHelper($this);
    $helper->confirmFileExists();
    $credit = $helper->_credit;
    $creditFile = $helper->_creditFile;

    // Confirm transaction integirty using the token stored in the session
    if ( $this->_checkToken($creditFile->getId()) ) 
    {
      $this->_storeToken();  // invalidate the token

      $success = $creditFile->delete();
    }
    if ($success)  // DONE!  re-direct back to section
    {
      $this->_flashMessage('File '. $this->view->filename .' was successfully deleted for credit '. $credit->getTitle() );
      $this->_redirect('/section/'. $credit->getSectionId() );
    }
    // else the deletefile view actually serves an error message: file not deleted
    $helper->initView('Delete Submission');
  }

  /**
   * Helper: Store a token in the session to verify the file being deleted.
   * @param $fileId the ID of the file requested for deletion.
   * 
   */
  private function _storeToken($fileId=null)
  {
    $this->_storeToSession('deleteThisFile', $fileId);
  }

  /**
   * Helper: Check a token for delete transaction integrity.
   * @param $fileId the Id of the file to check against delete request.
   */
  private function _checkToken($fileId)
  {
    return ( $fileId == $this->_getFromSession('deleteThisFile') );
  }

  /**
   * /credit/viewfile/?credit=#
   * This action should probably move to a fileController in future?
   * GET:  serve a PDF file for viewing with PDF browser plug-in
   * @param integer credit is the POID of CreditPdfFile to view
   */
  function viewfileAction()
  {
    $this->_downloadFile(new CreditFileActionHelper($this));
  }

  /**
   * /credit/savefile/?credit=#
   * This action should probably move to a fileController in future?
   * GET:  serve a PDF file for download to the client filesystem
   * @param integer credit is the POID of Credit to download file for
   */
  function savefileAction()
  {
    $this->_downloadFile(new CreditFileActionHelper($this));
  }
  
  /**
   * /credit/getfile/?creditfile=#
   * Allows direct access to credit file by ID - restricted to Admin users.
   * This action should probably move to a fileController in future?
   * GET:  serve a PDF file for download to the client filesystem
   * @param integer creditfile is the POID of CreditPdfFile to download
   */
  function getfileAction()
  {
    $this->_downloadFile(new DirectCreditFileActionHelper($this));
  }

  /**
   * Helper : download the requested file - only the header differs in the view
   * Should probably move to a fileController in future?
   * GET:  serve a PDF file for viewing with PDF browser plug-in
   * @param $helper - the CreditFileActionHelper object used for this download.
   */
  private function _downloadFile($helper)
  {
    $helper->confirmFileExists();
    $file = $helper->_creditFile;

    $this->view->filepath = $file->getFullPath();
    $this->view->filename = $file->getDisplayName();
    $this->view->realname = $file->getFileName();
    $this->_helper->layout->disableLayout(); // no layout for PDF views
  }

}


  /**
   * Helper Class: Perform initilazation for credit file action.
   * Should really be implemented as private inner-class, but no PHP support!
   *   Performs common initilization for actions that take a credit ID URL param.
   *   Loads the credit and associated file objects
   */
class CreditFileActionHelper extends STARS_ActionController
{
  /**#@+
   * Define labels passed to View.
   */
  const INSERT_LABEL = 'Credit File Upload';
  const UPDATE_LABEL = 'Re-submit : Credit File Upload';

  private $_controller;  // reference to the controller this helper is helping
  public $_credit;       // the credit being worked on (guaranteed)
  public $_creditFile;   // the credit file being contolled (may be null)
  
  /**
   * Initialize a Credit File Action.
   * Responsibilities: access control, retreive 'credit' URL param;
   *                   error handling on URL param
   */
  public function __construct(STARS_ActionController &$controller)
  {
    $controller->_protect(1);  // Access control: authenticated users only
    
    $this->_controller = $controller;
    
    $creditId = intval($controller->_getParam('credit'));
    $this->_credit = new STARS_Credit($creditId);
    
    if (! $this->_credit->isValidCredit()) 
    {
       throw new STARS_Exception('Invalid Credit');
    }
    
    // Load existing CreditFile object - this will be null for new uploads.
    $orgId = STARS_Person::getInstance()->get('orgid');  // restrict access to this org
    
    $this->_creditFile = STARS_CreditPdfFile::getCreditPdfFile($creditId, $orgId);
   }
   
   /**
    * If the file associated with this action must exist - call this method.
    * Responsibility: re-direct to error page if the file doesn't exist.
    */
   public function confirmFileExists()
   {
     if (! ($this->_creditFile && $this->_creditFile->fileExists()) )
     {
       throw new STARS_Exception('Invalid Credit File');
     }
   }
  
  /**
   * Helper: get an array with the correct legend label
   */
  public function getLegendLabel()
  {
    $label = $this->_creditFile?(self::UPDATE_LABEL):(self::INSERT_LABEL);
    return array('legendLabel' => $label);
  }

  /**
   * Set up some common view elements, including title, credit, filename
   */
  public function initView($titlePrefix)
  {
    $this->_controller->view->title = $titlePrefix .' for ' . $this->_credit->getTitle();

    $this->_controller->view->credit = $this->_credit->getCreditInfo();
    $this->_controller->view->credit['title'] = $this->_credit->getTitle();
    if ($this->_creditFile)
    {
      $this->_controller->view->filename = $this->_creditFile->getDisplayName();
    }
    $this->_controller->view->breadcrumb()
                            ->setSection($this->_credit->getSectionInfo());
  }
  
  /**
   * Set up the view fileoption element
   */
  public function addViewFileOptions()
  {
    $this->_controller->view->fileOptions = 
            self::_getFileOptions($this->_creditFile);
  }
  
  /**
   * Helper: Get user options (links) for managing existing file upload
   */
  public static function _getFileOptions($file)
  {
    if (! $file )
    {
      return null;   // no existing file - no options.
    }
    // Never pass the file id - it could be sub'ed for file not owned by user.
    // Pass the credit id, and we'll look-up the file for the user's org.
    return array(
          'filename' => $file->getDisplayName(),
          'viewURL'     => '/credit/viewfile/' . $file->getCreditId(),
          'saveURL'     => '/credit/savefile/' . $file->getCreditId(),
          'deleteURL'   => '/credit/confirmdelete/' . $file->getCreditId(),
    );
  }
}


  /**
   * Helper Class: Perform initilazation for direct-access credit file actions.
   *   Performs common initilization for actions that take a creditfile ID URL param.
   *   Loads the credit and associated file objects
   */
class DirectCreditFileActionHelper extends CreditFileActionHelper
{
  /**
   * Initialize a Direct-Access Credit File Action.
   * Responsibilities: access control, retreive 'credit' URL param;
   *                   error handling on URL param
   */
  public function __construct(STARS_ActionController &$controller)
  {
    $this->_controller = $controller;
    
    $controller->_protect(2);  // Access control: admin users only
    
    // In this case, we assume the url param is actually the credit file ID.
    $creditFileId = intval($controller->_getParam('credit'));
    $this->_creditFile = new STARS_CreditPdfFile($creditFileId);
    if (! $this->_creditFile->fileExists()) 
    {
       throw new STARS_Exception('Invalid Credit File - File does not exist');
    }

    $creditId = $this->_creditFile->getCreditId();
    $this->_credit = new STARS_Credit($creditId);

    if (! $this->_credit->isValidCredit()) 
    {
       throw new STARS_Exception('Invalid Credit for Credit File');
    }
  }
}
