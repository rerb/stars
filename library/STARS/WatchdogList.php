<?php
/**
 * WatchdogList simply pulls a list of recent entries from the Watchdog log table.
 *
 */
class STARS_WatchdogList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        $this->from('watchdog')
             ->limit(100)                        // grab only 100 most recent entries
             ->order('timestamp DESC');
    }
}
