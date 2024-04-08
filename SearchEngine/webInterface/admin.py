from django.contrib import admin
from .models import Pages, Keywords, Indexer

# Register your models here.
admin.site.register(Pages)
admin.site.register(Keywords)
admin.site.register(Indexer)

