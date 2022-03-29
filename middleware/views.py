from django.conf import settings
import json
import urllib.request

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from middleware.models import Title, Imdb


# ------------------------------------------ Routes ------------------------------------------


def fetch_all(request):
    """
    Fetches all titles from API & save in DB by looping through page number
    """
    # Get total number of pages
    pages = get_watchmode_pages_total()

    # Loop through pages & call API passing page number & persist
    for page in range(1, pages + 1):
        titles = call_watchmode_api(str(page))

        if titles is not None:
            save_watchmode_db(titles)

    return JsonResponse({'status': 'ok'})


def fetch_page(request, page):
    """
    Fetches all titles from API based on page number & save in DB
    """
    # Fetch specific page & save in DB
    titles = call_watchmode_api(str(page))
    save_watchmode_db(titles)

    return JsonResponse({'status': 'ok'})


def fetch_imdb_entry(request, imdb_id):
    """
    Fetches title details from IMDB API if it doesn't exist & save in DB
    """
    # Check if record already exist in db
    title_entry = Title.objects.get(imdb_id=imdb_id)
    imdb_entry = Imdb.objects.filter(title=title_entry).first()

    # if it doesn't exist, fetch from API & persists
    if imdb_entry is None:
        # Fetch all title from IMDB
        data = call_imdb_api(imdb_id)
        # Save in db
        save_imdb_title_db(data, title_entry)

    return JsonResponse({'status': 'ok'})


# ----------------------------------------------------------------------------------------------
# ------------------------------------------ Helpers -------------------------------------------
# ----------------------------------------------------------------------------------------------

# -------------------------------- Watchmode Helpers -------------------------------------------

def call_watchmode_api(page):
    WATCHMODE_URL = getattr(settings, "WATCHMODE_URL", None)
    WATCHMODE_API_CACHE_KEY = getattr(settings, "WATCHMODE_API_CACHE_KEY", None) + page

    titles = cache.get(WATCHMODE_API_CACHE_KEY)

    if not titles:
        # External API call
        # Source ID 203 is Netflix
        print(WATCHMODE_URL + "&source_ids=203&page=" + page)
        data = urllib.request.urlopen(WATCHMODE_URL + "&source_ids=203&page=" + page)
        titles = json.loads(data.read().decode())

        # Cache results for 2hr
        cache.set(WATCHMODE_API_CACHE_KEY, titles, 60 * 60 * 2)

    return titles


def save_watchmode_db(titles):
    for title in titles['titles']:
        name = title['title']
        year = title['year']
        imdb_id = title['imdb_id']
        tmdb_type = title['tmdb_type']
        title_type = title['type']

        values = {"title_name": name, "year": year, "imdb_id": imdb_id, "tmdb_type": tmdb_type, "type": title_type}

        # Upsert
        Title.objects.update_or_create(title_name=name, defaults=values)


def get_watchmode_pages_total():
    WATCHMODE_URL = getattr(settings, "WATCHMODE_URL", None)

    with urllib.request.urlopen(WATCHMODE_URL + "&source_ids=203") as url:
        data = json.loads(url.read().decode())
        pages_total = data['total_pages']
        return pages_total


# --------------------------------- IMDB Helpers -------------------------------------------

def call_imdb_api(title):
    IMDB_URL = getattr(settings, "IMDB_URL", None)
    url = IMDB_URL + title

    # imdb middleware blocks python from requesting (403 forbidden), a workaround is to fake a user-agent
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})

    with urllib.request.urlopen(req) as url:
        data = json.loads(url.read().decode())

    return data


def save_imdb_title_db(imdb, title_entry):
    image = imdb['image']
    runtimeStr = imdb['runtimeStr']
    plot = imdb['plot']
    directors = imdb['directors']
    imdb_rating = imdb['imDbRating']
    trailer = imdb['trailer']

    # Persist in DB
    imdb = Imdb(title=title_entry, image=image, runtimeStr=runtimeStr,
                plot=plot, directors=directors, imdb_rating=imdb_rating, trailer=trailer)

    return imdb.save()
