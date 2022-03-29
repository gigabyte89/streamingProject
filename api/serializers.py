from rest_framework import serializers

from middleware.models import Title, Imdb


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"


class ImdbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imdb
        fields = "__all__"
