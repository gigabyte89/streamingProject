from django.db import models


# Create your models here.
class Title(models.Model):
    title_name = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    imdb_id = models.CharField(max_length=200)
    tmdb_type = models.CharField(max_length=200)
    type = models.CharField(max_length=200)


class Imdb(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    image = models.CharField(null=True, max_length=200)
    release_date = models.DateField(null=True)
    runtimeStr = models.CharField(null=True, max_length=20)
    plot = models.TextField(null=True)
    directors = models.CharField(null=True, max_length=200)
    imdb_rating = models.CharField(null=True, max_length=4)
    trailer = models.CharField(null=True, max_length=200)
