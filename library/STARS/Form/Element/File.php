<?php
/**
 * Zend Framework
 *
 * LICENSE
 *
 * This source file is subject to the new BSD license that is bundled
 * with this package in the file LICENSE.txt.
 * It is also available through the world-wide-web at this URL:
 * http://framework.zend.com/license/new-bsd
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@zend.com so we can send you a copy immediately.
 *
 * @category   App
 * @package    App_Form_Element
 * @copyright  Copyright (c) 2008 Rob Allen (http://akrabat.com)
 * @license    http://akrabat.com/license/new-bsd     New BSD License
 * @version    $Id: $
 */


/**
 * @see Zend_Form_Element_Xhtml
 */
 require_once 'Zend/Form/Element/Xhtml.php';

/**
 * File Form Element
 *
 * Zend framework does not (yet) supply a built-in file upload form element.
 * @see http://akrabat.com/2008/04/07/simple-zend_form-file-upload-example/
 *
 * Zend Framework already provides a view helper for displaying a file element,
 * formFile, so we set the $helper member variable to 'formFile' so that the correct
 * element is rendered when the form is displayed. We then need to ensure that
 * validation is handled correctly. For all other form elements the value of the
 * field is returned in the POST array. For a file, this is not true as the data is
 * with the $_FILES global array. We could handle this in the controller, but by
 * putting it in the element class, we never have to think about it again.
 * The isValid() member function is used to set the value for an element and also run
 * the validator chain to determine if the value is valid or not.
 *
 * We override isValid() for the file element to provide two functionalities:
 *  - Set the value to the contents of correct sub-array of the $_FILES array .
 *  - Automatically turn on a custom validator called ValidFile which will check 
 *    if the upload succeeded.
 *
 * The file element also has some helper functions (setAutoInsertValidFileValidator
 * and getAutoInsertValidFileValidator) to control the auto-insertion of the
 * ValidFile validator. Note that if we do automatically insert the ValidFile
 * validator, then we turn off Zend_Form_Element's automatic NotEmpty validator
 * as it is redundant.
 *
 * Once we have set the $value variable correctly and inserted our validator, we call
 * up to the parent's isValid() function which will run the validation chain for us.
 */
class STARS_Form_Element_File extends Zend_Form_Element_Xhtml
{
    /**
     * Flag indicating whether or not to insert ValidFile validator when element is required
     * @var bool
     */
    protected $_autoInsertValidFileValidator = true;

    /**
     * Default view helper to use
     * @var string
     */
    public $helper = 'formFile';
    
    /**
     * Set flag indicating whether a ValidFile validator should be inserted when element is required
     * 
     * @param  bool $flag 
     * @return Zend_Form_Element
     */
    public function setAutoInsertValidFileValidator($flag)
    {
        $this->_autoInsertValidFileValidator = (bool) $flag;
        return $this;
    }

    /**
     * Get flag indicating whether a ValidFile validator should be inserted when element is required
     * 
     * @return bool
     */
    public function autoInsertValidFileValidator()
    {
        return $this->_autoInsertValidFileValidator;
    }
    
    
    public function isValid($value, $context = null)
    {
        // for a file upload, the value is not in the POST array, it's in $_FILES
        $key = $this->getName();
        if(null === $value) {
            if(isset($_FILES[$key])) {
                $value = new STARS_Form_Element_FileValue($_FILES[$key]);
            }
        }
        
        // auto insert ValidFile validator
        if ($this->isRequired()
            && $this->autoInsertValidFileValidator()
            && !$this->getValidator('ValidFile'))
        {
            $validators = $this->getValidators();
            $validFile   = array('validator' => 'ValidFile', 'breakChainOnFailure' => true);
            array_unshift($validators, $validFile);
            $this->setValidators($validators);
            
            // do not use the automatic NotEmpty Validator as ValidFile replaces it 
            $this->setAutoInsertNotEmptyValidator(false);
        }

        return parent::isValid($value, $context);
    }

}