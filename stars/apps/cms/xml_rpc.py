from stars.apps.helpers.xml_rpc import run_rpc
# from stars.apps.cms.models import Article, ArticleCategory

def get_article(nid):
    """
        Query drupal through XML-RPC to retrieve a single node
        nid
            the id of the node on the IRC to get
       return the node data dictionary containing node 'nid' or None
    """
    args = (int(nid), [])
    node_data = run_rpc('aashenode.get', args)
    return node_data

def get_article_list(category):
    """
        Query drupal through XML-RPC to return all nodes in a category
        category 
            the category defining which nodes to get from the IRC
        return a list of node_data dictionaries for articles in the category, or None
    """
    args = (category.term_id,)
    nodes = run_rpc('aashearticles.get', args)
    return nodes


def get_article_directory(category):
    """
        Query drupal through XML-RPC to return a directory of all nodes in a category
        category 
            the category defining which nodes to get from the IRC
        return a hierarchical directory of Articles in the category, or None
    """
    args = (category.term_id,)
    raw_directory = run_rpc('aashearticles.get_directory', args)
    return raw_directory

def get_childTerms(tid):
    """
        Query drupal through XML-RPC to return a list of terms or None
    """
    args = (tid,)
    return run_rpc('aashetaxonomy.get_childTerms', args)

def get_tree(tid):
    """
        Query drupal through XML-RPC to return a hierachical list of terms or None
    """
    args = (tid,)
    return run_rpc('aashetaxonomy.get_tree', args)


