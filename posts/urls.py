from django.urls import path

from . import views

urlpatterns = [
    path("404/", views.page_not_found, name="error404"),
    path("500/", views.server_error, name="error500"),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path("new/", views.NewPost.as_view(), name="new_post"),
    path("", views.index, name="index"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
]
