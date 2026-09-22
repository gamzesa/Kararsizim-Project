from django.urls import path

from . import views

urlpatterns = [
    path("", views.poll_list, name="poll_list"),
    path("anket/olustur/", views.poll_create, name="poll_create"),
    path("anket/<str:public_id>/", views.poll_detail, name="poll_detail"),
    path("anket/<str:public_id>/oy/", views.vote, name="vote"),
    path("anket/<str:public_id>/sil/", views.poll_delete, name="poll_delete"),
    path("anketlerim/", views.my_polls, name="my_polls"),
]
