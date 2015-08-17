from django import template
from adv_cache_tag.tag import CacheTag

class FileBasedCacheTag(CacheTag):

    class Meta(CacheTag.Meta):
        cache_backend = 'filecache'
        versioning = True

register = template.Library()
FileBasedCacheTag.register(register, 'file_cache')
