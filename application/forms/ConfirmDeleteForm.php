<?php
/**
 * Confirm Delete
 *  This form has a hidden token, used for transaction integrity.
 *
 * @package    STARS
 * @author     J. Fall
 * @version    0.1
 */


/**
 * Confirm a delete operation.
 * @param $token the token to place in a hidden field on the form.
 */
class forms_ConfirmDeleteForm extends STARS_Form 
{ 
    public function __construct($token, $options=null) 
    { 
         parent::__construct($options);
        
        // Hidden field to pass on a session token
        $hidden = new Zend_Form_Element_Hidden('token');
        $hidden->setRequired(true)
                       ->setvalue($token);

        $submit = new Zend_Form_Element_Submit('submit');
        $submit->setLabel('Delete');
        $submit->setDecorators(array('ViewHelper')); // don't decorate this button

        $this->addElements(array($hidden, $submit));
    } 
} 
