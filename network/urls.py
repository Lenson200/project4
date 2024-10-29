
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('upload_profile_image/',views.upload_profile_image, name='upload_profile_image'),
    #api routes
    path("edit/<str:post_id>", views.edit, name="edit"),
    path("like/<str:post_id>", views.like, name="like"),
    path("follow/<str:user_id>", views.follow, name="follow"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)