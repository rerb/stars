<?php

class STARS_UserList extends STARS_Abstract_SelectList
{
    public function __construct(array $options = array())
    {
        parent::__construct($options);
        
        // Grab all users from remote server where role is stars*
        // @todo Consider moving this to Person or User class?
        try {
            $client = STARS_User::getXmlRpcClient();
            $users = $client->getUsersByRole('stars');
        }
        catch (Zend_XmlRpc_Exception $e) {  
            print_r(e); exit;  // @todo  error handling for RPC failure.     
        }
        // Assumes records are returned in order: uid, name, mail, role
        $values = "";
        foreach ($users as $user) {
            $values .= "('" . implode("','", $user) . "'),";
        }
        $values = rtrim($values, ',');   // strip off the trailing comma

        // Create Temporary Table for the user data
        // @todo Consider moving this to an override version of the get method.
        try 
        {
            $db = Zend_Registry::get('db');
            $create = "CREATE TEMPORARY TABLE users (userid int, name varchar(40), mail text, role text)";
            $stmt = $db->query($create);
            
            $insert = "INSERT INTO users (userid, name, mail, role) VALUES $values";
            $stmt = $db->query($insert);
        }
        catch(Zend_Db_Statement_Mysqli_Exception $e)
        {
            print_r($e); exit;  // @todo 
        }
        
        // Get matching records from users join relperson2orgs join organizations join institutionnames join roles   
        //  - Do the 'where r.isdefault=1' in the Join so we get ALL users (even those not in relpersons2orgs yet)
        //  - Can't use 'personid=NULL ASC' to sort new users first b/c of quoting done by Zend_Db_Select
        $this->from(array('u' => 'users'), array('u.userid', 'u.name', 'u.mail', 'u.role'));
        $this->joinLeft(array('r'=>'relpersons2orgs'), 'r.personid = u.userid AND r.isdefault=1', array('r.personid', 'r.title', 'r.department'));
        $this->joinLeft(array('o' => 'organizations'), 'o.orgid = r.orgid', array());
        $this->joinLeft(array('n' => 'aashedata01.institutionnames'), 'o.nameid = n.id', array('orgname' => 'n.fullname'));
        $this->joinLeft('roles','roles.roleid = r.roleid', array('orgrole'=>'roles.role'));
        $this->order(array('role ASC', 'name ASC'));
    }
}
