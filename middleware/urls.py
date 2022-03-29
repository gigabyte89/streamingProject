from django.urls import path

from . import views

urlpatterns = [
    path('middleware/titles/', views.fetch_all),
    path('middleware/titles/<int:page>', views.fetch_page),
    path('middleware/title/<str:imdb_id>', views.fetch_imdb_entry),
]
