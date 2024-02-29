from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("lager", views.lager, name="lagerliste"),
    path("bestell", views.bestell, name="bestell_liste"),
    path("invest", views.invest, name="investmittel"),
    path("create_bestll", views.create_bestell, name="create_bestell"),
    path("create_lager", views.create_lager, name="create_lager"),
    path("handout_lager", views.handout_lager, name="handout_lager"),
    path("lager/<int:bestell_nr>", views.detail_lager, name="detail_lager"),
    path("<int:user_id>", views.profile, name="profile"),
    path("<int:user_id>/<int:bestell_nr>", views.detail_lager_profile, name="detail_lager_profile"),
    path("temp_lager", views.temp_lager, name="temp_lager"),
    path("temp_create_lager", views.temp_create_lager, name="temp_create_lager"),
    path("temp_handout_lager", views.temp_handout_lager, name="temp_handout_lager")
]
