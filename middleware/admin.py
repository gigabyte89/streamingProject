from django.contrib import admin
from . import models


# Register your models here.
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_name', 'year', 'imdb_id', 'tmdb_type', 'type',)


class IMDBAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'release_date', 'runtimeStr', 'imdb_rating', 'trailer',)


admin.site.register(models.Title, TitleAdmin)
admin.site.register(models.Imdb, IMDBAdmin)

