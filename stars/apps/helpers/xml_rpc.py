from django.conf import settings

import xmlrpclib, random, hashlib, hmac
from time import time
from stars.apps.helpers.exceptions import RpcException
from stars.apps.helpers import watchdog

def run_rpc(service_name, args):
    """
        Make an XML_RPC query to the given service on SSO_SERVER (AASHE IRC on Drupal)
        param
            service_name  the name of the service to invoke on the server
            args a tuple of arguments to be passed through to the service
        return
            the data returned by the service or None if it didn't exist
    """
    # Attempt to get the rpc service...
    server = get_server()
    if (not (isinstance(server, xmlrpclib.ServerProxy) and hasattr(server, service_name)) ):
        raise RpcException("No such service: %s" % service_name)

    service = getattr(server, service_name)
    result = ""
    # execute the RPC request
    try:
        hash_digest, domain, timestamp, nonce = get_params(service_name)
        if (settings.XMLRPC_USE_HASH):
            result = service(hash_digest, domain, timestamp, nonce,"????", *args)
        else:
            result = service(*args)
        return result
    except xmlrpclib.Fault, fault:
        # Attempting to distinguish b/w 404 and 500 here... not sure...
        if (fault.faultCode == 1):
            watchdog.log("XML-RPC", fault.faultString, watchdog.ERROR)
            return None
        else:
            raise RpcException(fault.faultString, "Resource is currently unavailable." )
    except xmlrpclib.ProtocolError, err:
        raise RpcException("%s"%err, "Internal Server Error")
    except Exception, e:
        watchdog.log("XML-RPC", "%s"%e, watchdog.ERROR)
        raise RpcException("%s"%e, "Resource is currently unavailable." )

    return None

def get_params(function_name):
    """
        Create the paramaters for the XML-RPC request
    """
    timestamp = str(time())
    nonce = str(random.uniform(1, 10))
    domain =  settings.STARS_DOMAIN  #"stars.dev.aashe.org"
    hash_params = [timestamp, domain, nonce, function_name]
    hashval = hmac.new(settings.SSO_API_KEY, ';'.join(hash_params), hashlib.sha256)

    return (hashval.hexdigest(), domain, timestamp, nonce)

def get_server():
    """
        Get the RPC server being used
    """
    return xmlrpclib.ServerProxy(settings.SSO_SERVER_URI, verbose=settings.XMLRPC_VERBOSE)
    
def list_methods():
    """
        Query Drupal for all available RPC methods
    """
    return get_server().system.listMethods()

def method_help(method):    
    """
        Query Drupal for help and parameters for a RPC method
    """
    server = get_server()
    help = server.system.methodHelp(method)
    params = server.system.methodSignature(method)
    return {'help':help, 'params':params}

"""
    Available Commands
    ['system.multicall', 'system.methodSignature', 'system.getCapabilities', 'system.listMethods', 'system.methodHelp', 'aasheuser.current', 'aasheuser.listbyrole', 'aasheuser.delete', 'aasheuser.get', 'aasheuser.login', 'aasheuser.logout', 'aasheuser.save', 'node.get', 'node.save', 'node.delete', 'user.delete', 'user.get', 'user.login', 'user.logout', 'user.save', 'node.all']
    
"""