<?php
/**
 * Stars Institutional Summary Report
 *
 * @category DB query
 * @package STARS
 * @author  J. Fall
 */
 
/**
 * STARS_SummaryReport
 * DB query to fetch summary status report for all institutions.
 */
class STARS_SummaryReport extends STARS_Abstract_SelectList
{
  /**
   * Construct a the query to select the list of institutional summary stat:
   * orgid, orgname, OP (creidts complete), AF (credits complete), 
   */
      public function __construct()
    {
        parent::__construct();
        $this->from('view_orgsummary');
        /*  The View used above is probably more efficient than the query below 
         *   in any case - here is the query, for posterity.
         ********************************************************************
        SELECT
            a.fullname AS orgname,
            COUNT(DISTINCT n1.datanormid) AS normAttempt,
            COUNT(DISTINCT n2.datanormid) AS normComplete,
            COUNT(DISTINCT f2.orgcreditfileid) as OP_credits,
            COUNT(DISTINCT f3.orgcreditfileid) as AF_credits,
            o.orgid
        FROM organizations o
        LEFT JOIN (aashedata01.institutionnames a) 
        ON (o.nameid = a.id)
        LEFT JOIN (
            orgcreditfiles f2,
            credits c2
        )
        ON (
            o.orgid = f2.orgid
            AND
            c2.creditid = f2.creditid
            AND
            c2.dicreditcategory = 2
        )
        LEFT JOIN (
            orgcreditfiles f3,
            credits c3
        )
        ON (
            o.orgid = f3.orgid
            AND
            c3.creditid = f3.creditid
            AND
            c3.dicreditcategory = 3
        )
        LEFT JOIN
            datanorm n1
        ON (
            o.orgid = n1.orgid
        )
        LEFT JOIN
            datanorm n2
        ON (
            o.orgid = n2.orgid
            AND
            n2.status = 2
        )
        GROUP BY
            o.orgid
        ORDER BY
            a.fullname
         ********************************************************************
         *  The following Zend query has a problem because the joinLeft method
         *   does not seem to allow multiple tables in a single join.
         *  BUT MYSQL definitely makes a distinction, and I can't figure out
         *   how to modify the query to make it work with the extra 2 joins.
         ********************************************************************
        $this->from(array('o' => 'organizations'), 'o.orgid');
        $this->joinLeft(array('a' => 'aashedata01.institutionnames'), 'o.nameid = a.id', new Zend_Db_Expr('a.fullname AS orgname'));
        $this->joinLeft(array('f2'=>'orgcreditfiles', 
                              'c2'=>'credits'), 
                        'o.orgid=f2.orgid AND c2.creditid=f2.creditid AND c2.dicreditcategory=2',
                        new Zend_Db_Expr('COUNT(DISTINCT f2.orgcreditfileid) AS OP_credits'));
        $this->joinLeft(array('f3'=>'orgcreditfiles', 
                              'c3'=>'credits'), 
                        'o.orgid=f3.orgid AND c3.creditid=f3.creditid AND c3.dicreditcategory=3',
                        new Zend_Db_Expr('COUNT(DISTINCT f3.orgcreditfileid) AS AF_credits'));
        $this->joinLeft(array('n1'=>'datanorm'), 'o.orgid=n1.orgid',
                        new Zend_Db_Expr('COUNT(DISTINCT n1.datanormid) AS normAttempt'));
        $this->joinLeft(array('n2'=>'datanorm'), 
                        'o.orgid=n2.orgid AND n2.status=2',
                        new Zend_Db_Expr('COUNT(DISTINCT n2.datanormid) AS normComplete'));
        $this->group('o.orgid');
        $this->order(array('a.fullname ASC')); 
       */
    }
}
