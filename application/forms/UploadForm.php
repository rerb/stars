<?php
/**
 * File Upload Form
 *
 * Adapted from
 *  http://devzone.zend.com/manual/features.file-upload.html
 *  http://akrabat.com/2008/04/07/simple-zend_form-file-upload-example/
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
 * @package    STARS
 * @copyright  Copyright (c) 2008 Rob Allen (http://akrabat.com)
 * @license    http://akrabat.com/license/new-bsd     New BSD License
 * @version    0.1
 */

/**
 * Form for uploading PDF files.
 * @param array $options may contain 'legendLabel' to label upload fieldset
 */
class forms_UploadForm extends STARS_Form 
{ 
    public function __construct($options=null) 
    { 
        $this->setName('upload');
        $this->setAttrib('enctype', 'multipart/form-data');
        
        $file = new STARS_Form_Element_File('file');
        $file->setLabel('File')
                 ->setRequired(true)
                 ->addPrefixPath('STARS_Validate', 'STARS/Validate/', 'validate')
                 ->addValidator('ValidStarsCreditFile');

        // Don't show points selector if the credit has no points.
        if ($options['pointsOptions']) {
          $points = new Zend_Form_Element_Select('points');
          $notEmpty = new Zend_Validate_NotEmpty();
          $notEmpty->setMessage('Please enter the estimated points for this credit',
                                 Zend_Validate_NotEmpty::IS_EMPTY);
          
          $points->setLabel('Estimated points for this credit')
                 ->setRequired(true)
                 ->addValidator($notEmpty)
                 ->setMultiOptions($options['pointsOptions']);
        }
        else {
          $points = new Zend_Form_Element_Hidden('points');
          $points->setValue('not applicable');
        }
/*
       $description = new Zend_Form_Element_Textarea('description');
        $description->setLabel('Optional : annotation for this submission')
                    ->setRequired(false)
                    ->setAttrib("rows","5");
*/
        $submit = new Zend_Form_Element_Submit('submit');
        $submit->setLabel('Upload');
        $submit->setAttrib('class', 'button');
        
        $this->addElements(array($file, $points, $submit));

        $this->addDisplayGroup(array('file', 'points', 'submit'), 'fileupload', array('legend'=>$options['legendLabel']));

        parent::__construct($options);
    } 
} 
