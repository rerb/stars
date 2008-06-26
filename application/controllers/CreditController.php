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
 *  /credit/deletefile/?id=# - Delete Credit PDF file #
 *
 * @package STARS
 * @subpackage controllers
 */
class CreditController extends STARS_ActionController
{
  // This should GO - it's only here to allow us to use layouts for these views.
  public function __construct(Zend_Controller_Request_Abstract $request, Zend_Controller_Response_Abstract $response, array $invokeArgs = array())
  {
    parent::__construct($request, $response, $invokeArgs);

    // Initialise Zend_Layout's MVC helpers
    // This should go in bootstrap if we choose to adopt using layouts.
    define ("ROOT_DIR",$_SERVER['DOCUMENT_ROOT'].'/..');
    //define('ROOT_DIR', dirname(dirname(dirname(__FILE__))));
    Zend_Layout::startMvc(array('layoutPath' => realpath(ROOT_DIR).'/application/views/layouts'));
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


    $form = new forms_UploadForm( $helper->getLegendLabel() );
    $this->_populateUploadForm($form, $creditFile);

    if ($this->_request->isPost()) 
    {
      $formData = $this->_request->getPost();
      if ($form->isValid($formData) &&
          $creditFile = $this->_storeData($form->getValues(), $credit) )
      { // DONE!  re-direct back to section dashboard
        $this->_flashMessage('File '.$creditFile->getDisplayName() .' was successfully uploaded for credit '.$credit->getTitle());
        $this->_redirect('/section/'. $credit->getCategoryId() );
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
  private function _storeData($data, $credit)
  {
    $orgId = STARS_Person::getInstance()->get('orgid');
    $file = STARS_CreditPdfFile::upload($data['file'], $credit->getId(), $orgId, $data['description']);
    return $file;
  }
  
  /**
   * Helper: re-populate upload form from creditPdfFile data
   */
  private function _populateUploadForm($form, $creditPdfFile)
  {
    if ($creditPdfFile)
    {
      $data = array(
        'description' => $creditPdfFile->getNotes(),
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
      $this->_redirect('/section/'. $credit->getCategoryId() );
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
   * /credit/viewfile/?id=#
   * This action should probably move to a fileController in future?
   * GET:  serve a PDF file for viewing with PDF browser plug-in
   * @param integer id is the POID of CreditPdfFile to view
   */
  function viewfileAction()
  {
    $this->_downloadFile();
  }

  /**
   * /credit/savefile/?id=#
   * This action should probably move to a fileController in future?
   * GET:  serve a PDF file for download to the client filesystem
   * @param integer id is the POID of CreditPdfFile to save
   */
  function savefileAction()
  {
    $this->_downloadFile();
  }

  /**
   * Helper : download the requested file - only the header differs in the view
   * Should probably move to a fileController in future?
   * GET:  serve a PDF file for viewing with PDF browser plug-in
   * @param integer id is the POID of CreditPdfFile to download
   */
  private function _downloadFile()
  {
    $helper = new CreditFileActionHelper($this);
    $helper->confirmFileExists();
    $file = $helper->_creditFile;

    $this->view->filepath = $file->getFullPath();
    $this->view->filename = $file->getDisplayName();
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
          'viewURL'     => '/credit/viewfile/?credit=' . $file->getCreditId(),
          'saveURL'     => '/credit/savefile/?credit=' . $file->getCreditId(),
          'deleteURL'   => '/credit/confirmdelete/?credit=' . $file->getCreditId(),
    );
  }
}