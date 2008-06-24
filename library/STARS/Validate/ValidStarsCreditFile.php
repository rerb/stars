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

    const NO_FILE = 'nofile';         //  there is not file
    const MIME_TYPE = 'mime';       // The uploaded file has the wrong mime type.
    const FILE_FORMAT = 'format';     // The uploaded file does not have the correct format.
    const ERROR = 'error';          // General error for future proofing against new PHP versions

    /**
     * @var array
     */
    protected $_messageTemplates = array(
        self::NO_FILE => "No Credit File was uploaded.",
        self::MIME_TYPE   => "The uploaded file is not a valid STARS Credit PDF file.",
        self::FILE_FORMAT => "The uploaded file is not a valid STARS Credit PDF file.",
        self::ERROR => "Unknown STARS Credit File Format error"
    );

    /**
     * Defined by Zend_Validate_Interface
     *
     * Returns true if there was a valid STARS Credit PDF file uploaded.
     * 
     * @note: This validator expects $value to be the array from $_FILES
     *
     * @param array $value
     * @return boolean
     * @todo peek inside file to check for valid STARS PDF file.
     */
    public function isValid($value)
    {
        $valueString = '';
        if((is_array($value) || $value instanceof ArrayObject) 
            && array_key_exists('tmp_name', $value)
            && is_uploaded_file($value['tmp_name']) ) {

            // set the %value% placeholder to the uploaded filename
            $valueString = $value['name'];
            $mimeType = $value['type'];
        }
        else {
           $this->_error(self::NO_FILE);
           return false;
        }
        
        $this->_setValue($valueString);

        // This is just for testing - we really want to look into the file
        // never mind the file extension - that's just so MS
        $ext = strtolower( substr($valueString, -3) );
        
        if ($ext != 'pdf') {
           $this->_error(self::FILE_FORMAT);
           return false;
        }
        else if ($mimeType != 'application/pdf')  
        { 
           $this->_error(self::MIME_TYPE);
           return false;
        }

        return true;
    }

}
