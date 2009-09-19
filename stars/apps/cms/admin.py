from django.contrib import admin

from stars.apps.cms.models import ArticleCategory

class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'term_id')
    prepopulated_fields = {'slug': ('label',)}

admin.site.register(ArticleCategory, ArticleCategoryAdmin)


