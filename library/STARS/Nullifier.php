<?php

class STARS_Nullifier
{
    public static function nullify($array)
    {
        foreach($array as $key => $value)
        {
            if($value == '')
            {
                $array[$key] = new Zend_Db_Expr('NULL');
            }
        }
        
        return $array;
    }
}
