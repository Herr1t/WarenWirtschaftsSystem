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
    path("rückgabe", views.rückgabe, name="rückgabe"),
    path("lager/<str:bestell_nr>", views.detail_lager, name="detail_lager"),
    path("lager/<str:bestell_nr>/löschen", views.löschen, name="löschen"),
    path("<int:user_id>", views.profile, name="profile"),
    path("<int:user_id>/<str:bestell_nr>", views.detail_lager_profile, name="detail_lager_profile"),
    path("bestell/<str:bestell_nr>", views.update, name="update_bestell"),
    path("lager_ohne", views.lager_ohne_invest, name="lager_ohne"),
    path("profile/<int:user_id>", views.profile_lager_ohne, name="profile_lager_ohne"),
    path("lager_ohne/<str:bestell_nr>", views.handout_lager_ohne, name="handout_lager_ohne"),
    path("<int:user_id>/detail_profile_lager_ohne/<str:bestell_nr>", views.detail_profile_lager_ohne, name="detail_profile_lager_ohne")
]
