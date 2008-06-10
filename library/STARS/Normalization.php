<?php

class STARS_Normalization extends STARS_Abstract_SelectRow
{
    public function __construct($datanormid)
    {
        parent::__construct();
        
        $this->from('datanorm');
        $this->where('datanormid = ?', intval($datanormid));
    }
}
