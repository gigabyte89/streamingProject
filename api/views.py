from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.views import APIView

import middleware
from api.serializers import TitleSerializer, ImdbSerializer
from middleware.models import Title, Imdb


class TitleList(APIView):

    def get(self, request):
        """
        Outputs all titles from DB
        """
        titles_list = Title.objects.all()
        serializer = TitleSerializer(titles_list, many=True)

        return Response(serializer.data)


class TitleDetailAPIView(APIView):
    # IMDB API says max of 100 per day - so I added Throttle in this view
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request, pk):
        """
        Outputs a title details from DB - or fetches it from imdb REST API if it doesn't exist
        """
        try:
            title_entry = Title.objects.get(pk=pk)

            # Fetch imdb remote API - Logic is in middleware app
            middleware.views.fetch_imdb_entry(request, title_entry.imdb_id)

            # Now fetch from db
            imdb_entry = Imdb.objects.get(title=title_entry)

        except Title.DoesNotExist:
            return Response({'error': 'Title not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Imdb.DoesNotExist:
            return Response({'error': 'Title Details not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ImdbSerializer(imdb_entry)
        return Response(serializer.data)


@api_view()
def titles_filters(request):
    """
    Outputs all titles from DB with year and/or type filter(s)
    """
    year = request.GET.get('year')
    title_type = request.GET.get('type')

    if year is not None and title_type is not None:
        titles_list = Title.objects.filter(year=year, tmdb_type=title_type)
    elif year is not None:
        titles_list = Title.objects.filter(year=year)
    elif title_type is not None:
        titles_list = Title.objects.filter(tmdb_type=title_type)

    serializer = TitleSerializer(titles_list, many=True)

    return Response(serializer.data)
