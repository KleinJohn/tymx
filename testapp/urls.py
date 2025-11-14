from django.urls import path

from testapp import views

app_name = "testapp"
urlpatterns = [
    path("test/", views.testview, name="testview"),
]
