from django.contrib.auth.models import User
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase

from middleware import models


class Title(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="example", password="examp@123")
        self.client.force_authenticate(user= self.user)

        # Create 2 titles
        self.title = models.Title.objects.create(title_name="Rescued by Ruby", tmdb_type="movie",
                                                 year="2022", type="movie", imdb_id="tt11278476", )
        self.title2 = models.Title.objects.create(title_name="Arcane", tmdb_type="tv",
                                                  year="2021", type="tv_series", imdb_id="tt11126994", )

        # Create 1 title details (imdb)
        self.imdb = models.Imdb.objects.create(
            image="https://imdb-api.com/images/original"
                  "/MV5BM2QzMWM5OTgtZDE1MC00ZmMyLWIyODItMmQ4NjNlZGRjYTUzXkEyXkFqcGdeQXVyMTEyMjM2NDc2._V1_Ratio0"
                  ".6751_AL_.jpg",
            runtimeStr="1h 46min",
            plot="Rescued by Ruby plot is a dog", release_date=None,
            title_id=self.title.id, directors="Doge",
            imdb_rating="7.4", trailer=None, )

    def test_get_all_titles(self):
        """
        Ensure we can list all titles
        """
        url = reverse('all-titles')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_get_all_titles_filters(self):
        """
        Ensure we can view titles with 2 filters; it should get 1 result
        """
        url = reverse('titles-filters') + "?year=2022&type=movie"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_title_details(self):
        """
        Ensure we can view a title details & check if it has 9 fields
        """
        url = reverse('title-detail', args=(self.title.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 9)

    def test_get_title_details_bad_request(self):
        """
        Ensure we get error message when viewing an invalid title details
        """
        url = reverse('title-detail', args=(1234567,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
