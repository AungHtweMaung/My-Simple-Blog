from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('blog/<int:id>', views.article, name="article"),
    path('search/', views.search, name="search"),
    path('profile/', views.profile, name="profile"),
    path('join/signup', views.signup, name="signup"),
    path('join/login', views.login, name="login"),
    path('join/logout', views.logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('manage/blog/create', views.create_article, name="create_article"),
    path('manage/blog/edit/<int:id>', views.edit_article, name="edit_article"),
    path('manage/blog/remove/<int:id>', views.remove_article, name="remove_article"),
    path('manage/blog/handlepublishing', views.handle_publishing, name="handle_publishing"),
]
