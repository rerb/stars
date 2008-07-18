<?php

/**
 * STARS/Validate/ValidStarsCreditFile.php
 *
 * @package    STARS_Validate
 * @author     J. Fall
 * @version    0.1
 */

/**
 * @see Zend_Validate_Abstract
 */
require_once 'Zend/Validate/Abstract.php';

/**
 * Validator for {@link StarsCreditFile} Form Element
 *
 * This class handles validating the contents of the file itself.  
 * It uses the ValidFile validator to ensure the file uploaded fine. 
 */
class STARS_Validate_ValidStarsCreditFile extends Zend_Validate_Abstract
{
    public $metaTag = '';  // required for validation messaging
    protected $_messageVariables = array(
        'credit' => 'metaTag'
    );
    
    const NO_FILE = 'nofile';         //  there is not file
    const MIME_TYPE = 'mime';         // The uploaded file has the wrong mime type.
    const MISMATCH = 'mismatch'; // The uploaded file does not match credit being submitted.
    const ERROR = 'error';          // General error for future proofing against new PHP versions

    /**
     * @var array
     */
    protected $_messageTemplates = array(
        self::NO_FILE   => "No Credit File was uploaded.",
        self::MIME_TYPE => "The uploaded file is not a valid STARS Credit PDF file.",
        self::MISMATCH  => "File '%value%' is not the correct STARS Credit Form for '%credit%'.",
        self::ERROR => "Unknown STARS Credit File Format error"
    );

    /**
     * Defined by Zend_Validate_Interface
     *
     * Returns true if there was a valid STARS Credit PDF file uploaded.
     * 
     * @note: This validator expects $value to be the array from $_FILES
     *
     * @param array $value - value to validate
     * @param array $context - form context, may contain 'STARSmetatag' element, used to validate file contents.
     * @return boolean
     * @todo peek inside file to check for valid STARS PDF file.
     */
    public function isValid($value, $context = null)
    {
        $valueString = '';
        if((is_array($value) || $value instanceof ArrayObject) 
            && array_key_exists('tmp_name', $value)
            && is_uploaded_file($value['tmp_name']) ) {

            $filename = $value['name'];
            $mimeType = $value['type'];
        }
        else {
           $this->_error(self::NO_FILE);
           return false;
        }
        
        // set the %value% placeholder to the uploaded filename
        $this->_setValue($filename);

        // This is just for testing - we really want to look into the file
        // never mind the file extension - that's just so MS
        $pathInfo = pathinfo($filename);
        if ('pdf' != $pathInfo['extension']) {
           $this->_error(self::MIME_TYPE);
           return false;
        }
        else if ($mimeType != 'application/pdf')  
        { 
           $this->_error(self::MIME_TYPE);
           return false;
        }

       // Finally - the real test: does the file contain the correct meta-data
       // tag for this credit (assuming teh credit came in with the context...)
       // If there is no credit in the context, I guess any file validates.
       if (! empty($context['STARS_credit'])) {
         $credit = $context['STARS_credit'];
         $this->metaTag = $credit->creditCode();

         if (! STARS_File::containsTag($value['tmp_name'], $this->metaTag)) {
           $this->_error(self::MISMATCH);
           return false;
         }
       }
       return true;
    }

}
