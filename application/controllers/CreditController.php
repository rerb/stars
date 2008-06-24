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
  /**#@+
   * Define labels passed to View.
   */
  const INSERT_LABEL = 'Credit File Upload';
  const UPDATE_LABEL = 'Re-submit : Credit File Upload';

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
   *  /credit/index
   *  What should this do??
   * @todo: redirect this to an Error controller?
   */
  public function indexAction()
  {
    $this->view->title = 'STARS Credits';
  }
  
  /**
   * /credit/upload/?credit=#
   * GET:  present file UploadForm to upload a PDF Credit file
   * POST: attempt to upload the user's file
   * @param integer id is the POID of Credit to upload file for
   * @todo error handling
   */
  function uploadAction()
  {
    $this->_protect(1);
    $orgId = STARS_Person::getInstance()->get('orgid');  // restrict access to this org
    
    $creditId = intval($this->_getParam('credit'));
    $credit = new STARS_Credit($creditId);

    if (! $credit->isValidCredit()) 
    {
       // TO DO: pass this to error handler instead.
       $this->view->pageTitle = "Error";
       $this->view->bodyCopy = "<p>Invalid Credit ID specified : " . $creditId . " - try again.</p>";
       return;
    }

    $this->view->title = 'Submission for ' . $credit->getTitle();
    $this->view->credit = $credit->getCreditInfo();
    $this->view->credit['title'] = $credit->getTitle();
    $this->view->error = false;

    // Load existing CreditFile object - this will be null for new uploads.
    $creditFile = STARS_CreditPdfFile::getCreditPdfFile($creditId, $orgId);

    $this->view->fileOptions = self::_getFileOptions($creditFile);

    $form = new forms_UploadForm( $this->_getLegendLabel($creditFile) );
    $this->_populateUploadForm($form, $creditFile);

    if ($this->_request->isPost()) 
    {
      $formData = $this->_request->getPost();
      if ($form->isValid($formData) &&
          $creditFile = $this->_storeData($form->getValues(), $creditId, $orgId) )
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
  private function _storeData($data, $creditId, $orgId)
  {
    $file = STARS_CreditPdfFile::upload($data['file'], $creditId, $orgId, $data['description']);
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
   * /credit/deletefile/?id=#
   * This action should probably move to a fileController in future?
   * This action uses a session token during the delete confirmation 
   * to ensure that delete confirmation transaction is legitimate.
   * GET:  display ConfirmDeleteForm
   * POST: attempt to delete the file with the given id
   * @param integer id is the POID of CreditPdfFile to delete
   * @todo Add error handling
   */
  function deletefileAction()
  {
    $this->_protect(1);
    $orgId = STARS_Person::getInstance()->get('orgid');  // restrict access to this org
    
    $fileId = intval($this->_getParam('id'));
    $creditFile = new STARS_CreditPdfFile($fileId, $orgId);
    $creditId = $creditFile->getCreditId();
    $credit = new STARS_Credit($creditId);
    // TO DO: error checking for invalid file / credit.

    $this->view->title = 'Delete Submission for ' . $credit->getTitle();
    $this->view->credit = $credit->getCreditInfo();
    $this->view->credit['title'] = $credit->getTitle();
    $this->view->fileOptions = self::_getFileOptions($creditFile);
    $this->view->filename = $creditFile->getDisplayName();
    $this->view->cancelAction = "/credit/upload/?credit=$creditId";
    $this->view->error = false;

    if ($this->_request->isPost()) // POST:
    {
      $formData = $this->_request->getPost();
      $success = false;
      // Confirm transaction integirty using the token stored in the form
      if ( $this->_checkToken($formData['token']) ) 
      {
        $this->_generateToken();  // invalidate the token

        $success = $creditFile->delete();
      }
      if ($success)  // DONE!  re-direct back to section
      {
        $this->_flashMessage('File '. $this->view->filename .' was successfully deleted for credit '. $credit->getTitle() );
        $this->_redirect('/section/'. $credit->getCategoryId() );
      }
      else  // Token did not match or credit could not be deleted for some reason.
      {  
        $this->view->error = true;
      }
    }
    else // GET: trow up the confirmation with a transaction integrity token
    {
      $form = new forms_ConfirmDeleteForm($this->_generateToken());
      $this->view->form = $form;
    }
  }

  /**
   * Helper: generate a random md5 session token - used to ID a transaction.
   *  credit: Evans (Guide to ... Zend Framework) p. 32
   *   This should be moved somewhere more general (functions.php?)
   */
  private function _generateToken($seed="43LKdfk*$#980ujfmo4")
  {
    $token = md5($seed.mktime());
    $globalSession = new Zend_Session_Namespace('global_data');
    $globalSession->token = $token;
    return $token;
  }

  /**
   * Helper: Check a token for transaction integrity.
   *  credit: Evans (Guide to ... Zend Framework) p. 32
   *   This should be moved somewhere more general (functions.php?)
   */
  private function _checkToken($token='')
  {
    $globalSession = new Zend_Session_Namespace('global_data');
    return !empty($token) && $token==$globalSession->token;
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
   * @todo Add error handling
   */
  private function _downloadFile()
  {
    $this->_protect(1);
    $orgId = STARS_Person::getInstance()->get('orgid');  // restrict access to this org
    $fileId = intval($this->_getParam('id'));
    $file = new STARS_CreditPdfFile($fileId, $orgId);
    // TO DO: error checking for invalid file.

    $this->view->filepath = $file->getFullPath();
    $this->view->filename = $file->getDisplayName();
    $this->_helper->layout->disableLayout(); // no layout for PDF views
  }

  /**
   * Helper: get an array with the correct legend label
   */
  private function _getLegendLabel($fileExists)
  {
    $label = $fileExists?(self::UPDATE_LABEL):(self::INSERT_LABEL);
    return array('legendLabel' => $label);
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
    return array(
          'filename' => $file->getDisplayName(),
          'viewURL'     => '/credit/viewfile/?id=' . $file->getId(),
          'saveURL'     => '/credit/savefile/?id=' . $file->getId(),
          'deleteURL'   => '/credit/deletefile/?id=' . $file->getId(),
    );
  }
}
