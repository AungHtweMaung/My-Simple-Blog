from django.contrib import admin
from .models import Author, Category, Article, Profile

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ['id',]

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Profile)