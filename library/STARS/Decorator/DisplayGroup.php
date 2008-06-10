<?php

class STARS_Decorator_DisplayGroup extends Zend_Form_Decorator_Abstract
{
    public function render($content)
    {
        $output = '<tr>'."\n";
        $output .= "\t".'<th colspan="2">'.$this->getElement()->getLegend().'</th>'."\n";
        $output .= '</tr>'."\n";
        
        return $output.$content;
    }
}
