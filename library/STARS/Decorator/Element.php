<?php

class STARS_Decorator_Element extends Zend_Form_Decorator_Abstract
{
    /**
     * Class name—calculated only once
     * @var string
     */
    private $_class;
    
    /**
     * True if required OR pseudo-required
     * @var bool
     */
    private $_notOptional;
    
    /**
     * Element view script filename
     * @var string
     */
    private $_viewScript;
    
    public function render($content)
    {
        $this->_setStarsProperties();
        
        $element = $this->getElement();
        
        if(empty($this->_viewScript))
        {
            if($element instanceof Zend_Form_Element_Textarea)
            {
                $this->_viewScript = 'textarea.phtml';
            }
        
            elseif($element instanceof Zend_Form_Element_Submit)
            {
                $this->_viewScript = 'submit.phtml';
            }
        
            elseif($element instanceof Zend_Form_Element_Hidden)
            {
                $this->_viewScript = 'hidden.phtml';
            }
            
            else
            {
                $this->_viewScript = 'default.phtml';
            }
        }
        
        $view = new Zend_View;
        $view->setScriptPath('../application/views/form/');
        $view->classes = $this->_buildClasses();
        $view->errors = $this->_buildErrors();
        $view->extra = $this->getElement()->getAttrib('extra');
        $view->input = $this->_buildInput();
        $view->label = $this->_buildLabel();
        
        return $content.$view->render($this->_viewScript);
    }
    
    private function _buildClasses()
    {
        $element = $this->getElement();
        
        $classes = array();
        
        if(count($element->getMessages()) > 0 and Zend_Controller_Front::getInstance()->getRequest()->isPost())
        {
            $classes[] = 'error';
        }
        
        if(($class = $element->getAttrib('class')) != 'required')
        {
            $classes[] = $class;
        }
        
        $classes[] = $this->_notOptional ? 'required' : 'optional';
        
        return implode(' ', $classes);
    }
    
    private function _buildDescription($descrip)
    {
        return '<img src="/img/help.png" class="help" onclick="help(this.parentNode, \''.str_replace(array("\n", '\''), array('\\n', '\\\''), $descrip).'\')">';
    }
    
    private function _buildErrors()
    {
        if(count($messages = $this->getElement()->getMessages()) == 0 or !Zend_Controller_Front::getInstance()->getRequest()->isPost())
        {
            return '';
        }
        
        return current($messages);
    }
    
    private function _buildInput()
    {
        $element = $this->getElement();
        
        $helper  = $element->helper;
        
        $attribs = $element->getAttribs();
        $attribs['class'] = $this->_class;
        unset($attribs['helper']); // Why is that an attribute?
        unset($attribs['starsViewScript']);
        unset($attribs['extra']);
        
        return $element->getView()->$helper
        (
            $element->getName(),
            ($element instanceof Zend_Form_Element_Submit) ? $element->getLabel() : $element->getValue(),
            $attribs,
            $element->options
        );
    }
    
    private function _buildLabel()
    {
        $element = $this->getElement();
        
        if($element instanceof Zend_Form_Element_Submit or $element instanceof Zend_Form_Element_Hidden)
        {
            return ' ';
        }
        
        $labelText = $element->getLabel();
        
        $label = $element->getView()->formLabel($element->getName(), $labelText, array('class' => $this->_class));        
        
        if($this->_notOptional)
        {
            $label .= ' <span class="required">Req</span>';
        }
        
        $descrip = $element->getDescription();
        
        if(!empty($descrip))
        {
            return $label.$this->_buildDescription($descrip);
        }
        
        return $label;
    }
    
    private function _setStarsProperties()
    {
        $this->_notOptional = ($this->getElement()->isRequired() or $this->getElement()->getAttrib('class') == 'required');
        $this->_viewScript = issetor($this->getElement()->getAttrib('starsViewScript'));
        $this->_class = $this->_buildClasses();
    }
}
