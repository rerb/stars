import time
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from stars.apps.cms import xml_rpc
from stars.apps.helpers import watchdog

# Content Management System for STARS static pages
# @todo: Use Django's object caching to cache all xml-rpc objects.
 
class ArticleCategory(models.Model):
    """
        Content Categories for static articles.
        These categories are loaded from a taxonomy on the IRC via an XML-RPC request
        The tree root for the hierarchical taxonomy is ARTICLE_BASE_TERM_ID
        Caching is used to store them locally.
    """
    label = models.CharField(blank=False, max_length=25)  # name of associated term in IRC
    slug = models.SlugField()
    ordinal = models.IntegerField(default=0)     # weight of associated term in IRC
    term_id = models.IntegerField(unique=True, primary_key=True)   # tid for associated term in IRC
    description = models.TextField()
    depth = models.IntegerField(default=0)
    parent_term = models.IntegerField(null=True)         # tid for parent term in IRC
    
    class Meta:
        ordering = ['depth', 'ordinal']
        verbose_name_plural = "categories"
    
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        articleCategories_set_defaults(self)
                
    def __unicode__(self):
        return self.label
    
    def get_parent(self):
        """ Return the parent category of this category or None for top-level category """
        if (self.depth !=0 and self.parent_term != None):
            return ArticleCategory.objects.get(term_id=self.parent_term)
        else:
            return None
        
    def __eq__(self, other):
        """ return true if other is an ArticleCategory for the same category."""
        if isinstance(other, ArticleCategory) :
            return other.term_id == self.term_id
        else:
            return False
        
    def get_root_category(self):
        """ 
            return the depth 0, top-level category for this category 
            For now, this assumes only a 2-level hierarchy (as does a bunch of other code!!)
            ... but this could be changed later.
        """
        root = self.get_parent()
        if (root != None):
            return root
        else:
            return self
        
    def get_absolute_url(self):
        return "/%s/%s/" % (settings.ARTICLE_PATH_ROOT, self.slug)
        
    def set_default_slug(self):
        self.slug = self.label.strip().lower().replace(" & ", "-").replace(" ", "-")

def articleCategories_sync():
    """ 
        Re-freshes cache (contents of the ArticleCategory table) from the IRC 
        returns a list of errors or [] on success.
    """
    term_dict = xml_rpc.get_tree(settings.ARTICLE_BASE_TERM_ID)
    errors = [] 
    for term in term_dict :
        try :
            ArticleCategory.objects.create(term_id=term["tid"], label=term["name"], 
                                           ordinal=term["weight"], depth=term["depth"],
                                           description=term["description"],
                                           parent_term=term["parents"][0])
        except IntegrityError:
            errors.append("Note: Article sub-category %s has multiple parent categories" % (term["name"]))
        except Exception, e:
            errors.append("%s error saving article category %s : %s" % (e.__class__.__name__, term["name"], e))
    return errors

def articleCategories_perform_consistency_check():
    """
        Perform a consistency check on Article Categories between the
        STARS cache and the IRC taxonomy. 
        Return a table comparing IRC terms with STARS categories: {'term', 'cat', 'consistent'}
          and True if STARS is completely consistent with the IRC, false if there is at least one inconsistency.
    """
    cached_categories = ArticleCategory.objects.all()
    IRC_term_dict = xml_rpc.get_tree(settings.ARTICLE_BASE_TERM_ID)
    # Remove duplicates caused by multi-parent hierarchy
    IRC_term_dict = [term for term in IRC_term_dict if term not in locals()["_[1]"]]  # See: http://code.activestate.com/recipes/204297/

    # Create a table and look for inconsistencies b/w the two lists
    category_table=[]
    is_consistent=True
    matched_cats = set()
    for term in IRC_term_dict :
        try:
            cat = cached_categories.get(term_id=term['tid'])
        except ObjectDoesNotExist:  # missing category from cache
            category_table.append({'term':term, 'cat':None, 'consistent':False})
            is_consistent = False
        else:  # all is well - terms match
            category_table.append({'term':term, 'cat':cat, 'consistent':True})
            matched_cats.add(cat)
    # Handle extra cached categories not found on the IRC
    excess_cats = set(cached_categories).difference(matched_cats)
    for cat in excess_cats:
        category_table.append({'term':None, 'cat':cat, 'consistent':False})
        is_consistent = False
                    
    return category_table, is_consistent

def articleCategories_get_top_level_categories():
    """ Return a list of just the depth 0 or top-level categories """
    return ArticleCategory.objects.filter(depth=0)
    
def articleCategories_set_defaults(instance, **kwargs):
    """ Fill and "default" fields for a category just created"""
    if (instance.slug == "" or instance.slug == None) :
        instance.set_default_slug()
    if (instance.parent_term == settings.ARTICLE_BASE_TERM_ID):
        instance.parent_term=None
         
models.signals.pre_save.connect(articleCategories_set_defaults, sender=ArticleCategory)
        
class Article(object):
    """
        One static article or page.
        Articles are not stored in the STARS DB and are not
        Django Models.  They are managed and stored in the IRC
        and pulled in using XML-RPC.  
        The primary job of this class is to package the node data
        returned by Drupal and hide its representation.
        Caution: objects of type Aricle will not always have all their
        attributes defined, depending on how they were retrieved!
    """
    # Node data is returned from Drupal in a dict.
    
    # Minimum fields:
    #    nid
    #    title
    # Other possible fields:
    #    teaser or body
    #    changed - date modified
    #    tid and vid (term and vocabulary ids)
    #    term - term label   

    def __init__(self, node_id, category):
        """
            Articles are constructed with :
            node_id
                the id of the article, typically fetched from Drupal through an XML-RPC request
            category
                the ArticleCategory this Article is being displayed within.  Since an article can have
                multiple categories, we need to know which one is currently "active"
            Throws ObjectDoesNotExist and XML_RPC excepetions
        """
        self.category = category
        #  not sure why the int cast is needed - url conf should pass an interger, but it doesn't.  hmmmm.
        node_data = xml_rpc.get_article(node_id)
        if (node_data == None):
            watchdog.log("CMS", "Attempt to get Article object %s failed" %  node_id, watchdog.NOTICE)
            raise ObjectDoesNotExist("No Article matching query found")
        self.__dict__.update(node_data)
               
    def get_modified_date(self):
        if (hasattr(self, "changed")) :
            date = self.changed
        elif (hasattr(self, "created")) :
            date = self.created
        else :
            date = None
        return time.ctime(int(date))
        
    def get_absolute_url(self):
        return "%s%s/" % (self.category.get_absolute_url(), self.nid)

    def get_edit_url(self):
        return "http://%s/node/%s/edit/" % (settings.IRC_DOMAIN, self.nid)

    def get_parent(self):
        """ Return the parent category of this article or None if error """
        return self.category
 
    def __str__(self):
        """ String representation of the article """
        if (hasattr(self, "title")) :
            return self.title
        elif (hasattr(self, "teaser")) :
            return self.teaser
        elif (hasattr(self, "body")) :
            return self.body
        elif (hasattr(self, "nid")) :
            return "Article, nid=%s" % self.nid
        else :
            return "Article - undefined"

class ListArticle (Article):
    """
        This is JUST an Article, but with a different constructor (here's a flaw in Python!)
        This class is basically private - clients should use the Article base class
        It is used for constructing an ArticleList object without making multiple RPC requests
    """
    def __init__(self, node_data, category):
        """
            ListArticles are constructed with :
            node_data
                a dictionary of fields, typically returned by Drupal through an XML-RPC request
                The actual fields will vary depending on how the request to Drupal was made.
            category
                the ArticleCategory this Article is being displayed within.  Since an article can have
                multiple categories, we need to know which one is currently "active"
        """
        self.__dict__.update(node_data)
        self.category = category

class ArticleList(list):
    """
        A list of Article objects.  Simple!
        Usually, this will be a list of all articles within an ArticleCateogry
        Throws ObjectDoesNotExist and XML_RPC excepetions
    """
    def __init__(self, category):
        """
            ArticleListss are constructed with :
            category
                the ArticleCategory this should create a list of articles for.
        """
        self.category = category
        nodes = xml_rpc.get_article_list(category)
        if (nodes == None or len(nodes) == 0) :
            watchdog.log("CMS", "Attempt to get AticleList object %s failed" %  category.label, watchdog.NOTICE)
            # don't raise an exception here - we'll just show an empty list of articles.
            nodes = []
        
        for node_data in nodes:
            self.append(ListArticle(node_data, category))

    def get(self, attr):
        """ Return a collection of same-named attribute values from this list """
        return Collection([getattr(x, attr) for x in self if hasattr(x, attr)])
    
    def call(self, fn, *args, **kwargs):
        """ Return the result of calling fn(args, kwargs) on each of the list elements """
        fns = self.get(fn)
        return Collection([x(*args, **kwargs) for x in fns if callable(x)])

class ArticleMenu(object):
    """
        A hierachical menu for articles within an ArticleCategory
        Articles and sub-categoryies are not stored in the STARS DB and are not
        Django Models.  They are managed and stored in the IRC
        and pulled in using XML-RPC.  
        The primary job of this class is to package the directory data
        returned by Drupal and hide its representation.
    """

    def __init__(self, category):
        """
            ArticleMenu is constructed with :
            category
                the ArticleCategory to create a menu for
            Fails silently - logs error, but returns an empty menu object
        """
        self.mm_category = category.get_root_category()
        directory = xml_rpc.get_article_directory(self.mm_category)
        if (directory == None or len(directory) == 0) :
            watchdog.log("CMS", "Attempt to get ArticleMenu for category %s failed" %  category.label, watchdog.ERROR)
            # don't raise exception here - page can be shown without the menu.
        
        # create the subcategory objects (a list of Articles for each subcategory)
        self.subcategories = []
        for subcat_data in directory:
            try:
                subcategory = ArticleCategory.objects.get(term_id=subcat_data['tid'])
                subcategory.articles = []
                for article_data in subcat_data['articles']:
                    subcategory.articles.append( ListArticle(article_data, subcategory) )
                self.subcategories.append(subcategory)
            except ObjectDoesNotExist, e:
                watchdog.log("CMS", "ArticleCategory %s does not exist - DB is probably out of sync with IRC, try syncdb"%subcat_data['name'], watchdog.ERROR)
            except Exception, e:
                watchdog.log_exception(e)
                