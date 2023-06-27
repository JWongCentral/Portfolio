from django.urls import path
from . import views

urlpatterns = [
    path("",views.main,name="main"),
    path("expertise", views.expertise, name="expertise"),
    path("resume", views.resume, name="resume"),
    path("projects", views.projects, name="projects"),
    path("contact", views.contact, name="contact"),
    path("projects/minesweeper", views.minesweeper, name = "minesweeper"),
    path("projects/minesweeper/get", views.minesweeper_get, name="minesweeper_get"),
    path("projects/minesweeper/post", views.minesweeper_post, name="minesweeper_post"),


]