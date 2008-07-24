<?php

header('Content-type: text/xml');

if(!isset($_GET['search']))
{
    exit;
}

echo file_get_contents('http://www.aashe.org/pcc/reports/fullname-search-xml.php?search='.urlencode($_GET['search']));
