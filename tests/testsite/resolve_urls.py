import os
import django
from django.urls import resolve, Resolver404

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testsite.settings")
django.setup()

urls_to_resolve = ["/bulma/index/", "/bulma/"]

for url in urls_to_resolve:
    try:
        match = resolve(url)
        print(f"URL: {url} -> View Name: {match.view_name}")
    except Resolver404:
        print(f"URL: {url} -> 404 Not Found")
    except Exception as e:
        print(f"URL: {url} -> Error: {str(e)}")
