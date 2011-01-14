#!/usr/bin/env python

"""
    Tests the connection with Drupal's xml-rpc services
    for authentication and content management
    
    usage: python manage.py execfile tests/xmlrpc.py
"""
from django.conf import settings
from stars.apps.auth.aashe import AASHEAuthBackend
from stars.apps.helpers import xml_rpc
from stars.apps.auth import xml_rpc as auth_rpc
from stars.apps.cms import xml_rpc as cms_rpc

print "URI: %s" % settings.SSO_SERVER_URI

print xml_rpc.get_server()

print "---------------LIST METHODS -------------------------"
print xml_rpc.list_methods()

## auth tests have been converented into doctests
auth = AASHEAuthBackend()

print "---------------TESTING AUTH -------------------------"
print auth.authenticate("it@aashe.org", "ba7que")
#print auth.logout()
print auth.authenticate("bens@aashe.org", "bjamin12")

#print "---------------TESTING GETBYEMAIL -------------------------"
print auth_rpc.get_user_by_email('it@aashe.org')
#
## @todo: convert these to doctests once data is stable on IRC
#print "---------------TESTING GETNODE ----------------------------"
## print xml_rpc.method_help("node.get")
##print cms_rpc.get_article(3971)
#
## print "---------------TESTING GETCHILDTERMS ----------------------------"
## print xml_rpc.method_help("aashetaxonomy.get_childTerms")
#terms = cms_rpc.get_childTerms(settings.ARTICLE_BASE_TERM_ID) 
#for term in terms:
#    print "Term: %s (%s) \t Weight: %s" % (term["name"], term["tid"], term["weight"])   
#    print "      %s" % term['description']      
#
#print "---------------TESTING GETTREE ----------------------------"
## print xml_rpc.method_help("aashetaxonomy.get_tree")
#term_tree = cms_rpc.get_tree(settings.ARTICLE_BASE_TERM_ID) 
#for term in term_tree :
#    print "Term: %s (%s) \t Weight: %s \t Depth : %s \t Parent: %s" % (term["name"], term["tid"], term["weight"], term["depth"], term["parents"][0])   
#    print "      %s" % term['description']  
#
#print "---------------TESTING GETARTICLEDIRECTORY----------------------------"
#category = ArticleCategory.objects.get(slug="about")
## print xml_rpc.method_help("aashearticles.get_directory")
#term_tree = cms_rpc.get_article_directory(category) 
#for term in term_tree :
#    print "Term: %s (%s) \t Weight: %s " % (term["name"], term["tid"], term["weight"])   
#    print "      %s" % term['description']  
#    print term['articles']
#    


