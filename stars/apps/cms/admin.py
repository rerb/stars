from django.contrib import admin

from stars.apps.cms.models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','published', )
    prepopulated_fields = {'slug': ('title',)}
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'parent')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('parent',)
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(Subcategory, SubcategoryAdmin)

class NewArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'timestamp',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('categories','subcategories')
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(NewArticle, NewArticleAdmin)


