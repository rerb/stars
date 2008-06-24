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
 * @see http://akrabat.com/2008/05/16/simple-zend_form-file-upload-example-revisited/
 * 
 * If the form fails to validate for some reason, then you get a nasty error:
 * Warning: htmlspecialchars() expects parameter 1 to be string, ...
 *
 * Essentially, what is happening is that the App_Form_Element_File class that we 
 * wrote assigns the $_FILES array to the $value parameter for the form element. 
 * On redisplay of the form, the formFile view helper then calls the escape() view 
 * helper passing in the $value when rendering the <input> element. The escape() 
 * view helper calls htmlspecialchars() which throws the warning about $value not
 * being a string.
 *
 * What we need is something that's an array when the data is valid, but can also
 * look like a string to htmlspecialchars(). This got me thinking about the SPL and
 * creating an object for the data from the $_FILES array.
 *
 * App_Form_Element_FileValue IS that class!
 */
class STARS_Form_Element_FileValue extends ArrayObject
{
    public function __toString()
    {
        $result = '';
        if(isset($this->name)) {
            $result = $this->name;
        }
        return $result;
    }
}
