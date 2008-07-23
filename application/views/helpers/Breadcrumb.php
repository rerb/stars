<?php
/**
 * STARS View Helper Breadcrumb
 *
 * @category View Helper
 * @package STARS
 * @author  J. Fall  (after http://www.nabble.com/Breadcrumb-view-helper-in-MVC--td17354631.html)
 */
 
/**
 * STARS Zend_View_Helper_Breadcrumb
 * View Helper class to load breadcrumbs from a config file and retrieve them.
 * @to-do implement this as a real view helper
 */
class Zend_View_Helper_Breadcrumb
{
  public $view;                       // the view that this helper helps
  protected $_section;                // optional: STARS Credit Tracker section
  protected static $_separator = '/'; // breadcrumb path separator
  
  /**
   * Get the breadcrumb for the current view.
   * @return string escaped HTML breadcrumb, based on current Controller/Action
   */
  public function breadcrumb()
  {
      return $this;
  }
  
  /**
   * Set the STARS Credit Tracker section to use for this breadcrumb
   *   This is a bit of a hack, but prevents duplicating data from the DB
   * @param array $section section information ('id', 'title') (for section sub-items)
   */
  public function setSection($section)
  {
    $this->_section = $section;
  }
  
  /**
   * This gets called by Zend so we have a copy of the View itself
   *  that this helper is helping.
   */
  public function setView(Zend_View_Interface $view)
  {
    $this->view = $view;
  }
  
  /**
   * Load the breadcrumb configuration file representing the site hierarchy.
   * Assumes breadcrumb is used only once - otherwise should use lazy read approach.
   */
  private function _getTree($controller, $action)
  {
    $iniSections = array('breadcrumb');
    if ($action) {  // only load the controller's leaf paths if there is an action
      $iniSections[] = $controller;
    }
    return new Zend_Config_Ini('../config/breadcrumb.ini', $iniSections);
  }

  /**
   * Get the breadcrumb for the current Controller/Action
   * @return array with items to list in the breadcrumb
   * @throws exception if an inconsistency in the configuration is found
   */
  private function _getCrumb()
  { 
    // retreive current controller and action
    $request  = Zend_Controller_Front::getInstance()->getRequest(); 
    $controller = $request->getControllerName();
    $action = $request->getActionName();
    if ($action == 'index' || $controller == 'error') {
      $action = null;
    }

    // Load the path tree from configuration file
    $tree = $this->_getTree($controller, $action);
    $item = ($action==null)?$controller:$action; 
     
    if (!isset($tree->$item)) {
      return;  // To Do: this is probably an internal error - throw exception?
    }
    $isLeaf = true; // $item should be the leaf - last item in the breadcrumb

    $crumb = array();
    do {
      $title = $tree->$item->title;
      // default url may be overridden...
      $url = isset($tree->$item->url) ? $tree->$item->url : ('/'.$item);
      
      // Bit of a hack here so that sections don't need to be hard-coded...
      if ($item == 'section' && $this->_section) {
        $title = $this->_section['title'];
        $url = $url . '/' . $this->_section['id'];
      }
      $crumb[] = array (
                        'url'    => $url,
                        'title'  => $title,
                        'link' => !$isLeaf,
                       );
      $isLeaf = false;
    } while (isset($tree->$item->parent) &&
             $item = $tree->$item->parent);
    return array_reverse($crumb);
  }

  /**
   * Render this breadcrumb
   * @return string containing the HTML for this breadcrumb
   */
  public function render()
  {
    $crumb = $this->_getCrumb();
    $sep = self::$_separator;

    $items = array();

    foreach($crumb as $element) {
      $url = $this->view->escape($element['url']);
      $title = $this->view->escape($element['title']);
      if ($element['link']) {
        $items[] = "<a href='{$url}'>{$title}</a>";
      }
      else {
        $items[] = $title;
      }
    }

    $xhtml = join(" {$sep} ", $items);

    return $xhtml;
  }
}