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
  private $_tree = null;              // data structure loaded from config file.
  private $_crumb = null;             // the crumb array itself.
  
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
   * Load the breadcrumb configuration file representing the site hierarchy,
   *  and sets the 'leaf node' based on current controller/action
   * @return arrary of objects: tree structure containing the breadcrumb.
   *    tree['tree'] contains the hierarchy itself
   *    tree['leaf'] contains name of leaf node object, or last item in the crumb.
   */
  private function _getTree()
  {
    // Lazy init - create on first call only...
    if ($this->_tree == null) {
      // We need to know the current path to retieve its crumb...
      $request  = Zend_Controller_Front::getInstance()->getRequest(); 
      $controller = $request->getControllerName();
      $action = $request->getActionName();
      if ($action == 'index' || $controller == 'error') {
        $action = null;
      }

      // Load the breadcrumb hierachy from the config file...
      $iniSections = array('breadcrumb', 'dashboard');
      if ($action != NULL) {  // only load the controller's leaf paths if there is an action
        $iniSections[] = $controller;
      }
      try {
          $tree = new Zend_Config_Ini('../config/breadcrumb.ini', $iniSections);
      }
      catch (Exception $e) {
          watchdog('defect','Error loading breadcrumb: '.$e->getMessage(), WATCHDOG_ERROR);
          // We can recover from this error - just don't display any breadcrumb...
          $tree = null;   
      }
      // Set object name of last node in crumb (leaf node of the tree)
      $leaf = ($action==null)?$controller:$action;
      
      $this->_tree = array('leaf'=>$leaf,'tree'=>$tree);
    }
    return $this->_tree;
  }

  /**
   * Get the breadcrumb for the current Controller/Action
   * Should not be called until ready to render!
   * @return array with items to list in the breadcrumb, 
   *         or NULL if an inconsistency in the configuration is found
   */
  private function _getCrumb()
  { 
    // Lazy init - create the crumb only if this is the first call...
    if ($this->_crumb == null) {
      // get the crumb hierarchy
      
      $tree = $this->_getTree();
      $item = $tree['leaf']; 
      $tree = $tree['tree'];

      $isLeaf = true; // $item should be the leaf - last item in the breadcrumb

      $crumb = array();
      do {
        if (!isset($tree->$item)) {
          return $crumb;  // To Do: this represents an internal error - log it?
        }
        
        $title = $tree->$item->title;
        // default url '/$item', may be overridden by config...
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
      $this->_crumb = array_reverse($crumb);
    }
    return $this->_crumb;
  }

  /**
   * Get the title for the leaf node of this breadcrumb
   * @return string containing the text title of the leaf node of the breadcrumb.
   */
  public function getTitle()
  {
    $tree = $this->_getTree();

    $title = isset($tree['tree']->$tree['leaf']->title) ?
                   $tree['tree']->$tree['leaf']->title : NULL;
    return $title;
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