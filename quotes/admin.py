from django.contrib import admin
from .models import Author, Quote, Topic, Keyword

# Register your models here.

admin.site.register(Author)
admin.site.register(Quote)
admin.site.register(Topic)
admin.site.register(Keyword)
