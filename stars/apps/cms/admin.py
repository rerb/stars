from django.contrib import admin

from stars.apps.cms.models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','published', )
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'parent')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('parent',)
admin.site.register(Subcategory, SubcategoryAdmin)

class NewArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created', 'changed', 'stamp')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('categories','subcategories')
admin.site.register(NewArticle, NewArticleAdmin)


