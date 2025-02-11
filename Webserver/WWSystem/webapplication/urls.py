from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("pw_reset", views.pw_reset, name="pw_reset"),
    path("lager", views.lager, name="lagerliste"),
    path("bestell", views.bestell, name="bestell_liste"),
    path("csv", views.some_view, name="csv"),
    path("download/<int:download_id>/", views.download, name="download"),
    path("invest", views.invest, name="investmittel"),
    path("invest/<int:klinik_ou>", views.detail_invest, name="detail_investmittel"),
    path("invest_soll", views.invest_soll, name="investmittel_soll"),
    path("invest_soll/<int:ou>", views.detail_invest_soll, name="detail_investmittel_soll"),
    path("invest_soll/<int:ou>/create_invest_soll", views.create_invest_soll, name="create_investmittel_soll"),
    path("invest_soll/<int:ou>/<int:id>/update_detail_invest_soll", views.update_detail_invest_soll, name="update_detail_invest_soll"),
    path("create_bestell", views.create_bestell, name="create_bestell"),
    path("create_lager", views.create_lager, name="create_lager"),
    path("handout_lager", views.handout_lager, name="handout_lager"),
    path("rückgabe", views.rückgabe, name="rückgabe"),
    path("lager/<str:bestell_nr>", views.detail_lager, name="detail_lager"),
    path("lager/<str:bestell_nr>/handout_lager_all", views.handout_lager_all, name="handout_lager_all"),
    path("lager/<str:bestell_nr>/löschen", views.löschen_lager, name="löschen_lager"),
    path("bestell/<str:bestell_nr>/löschen", views.löschen_bestell, name="löschen_bestell"),
    path("<int:user_id>", views.profile, name="profile"),
    path("<int:user_id>/achievements", views.achievements, name="achievements"),
    path("<int:user_id>/<str:bestell_nr>", views.detail_lager_profile, name="detail_lager_profile"),
    path("bestell/<str:bestell_nr>", views.update, name="update_bestell"),
    path("lager_ohne", views.lager_ohne_invest, name="lager_ohne"),
    path("profile/<int:user_id>", views.profile_lager_ohne, name="profile_lager_ohne"),
    path("lager_ohne/<str:bestell_nr>", views.handout_lager_ohne, name="handout_lager_ohne"),
    path("<int:user_id>/detail_profile_lager_ohne/<str:bestell_nr>", views.detail_profile_lager_ohne, name="detail_profile_lager_ohne"),
    path("lager_ohne/<str:bestell_nr>/löschen_lager_ohne", views.löschen_lager_ohne, name="löschen_lager_ohne"),
    path("test", views.test, name="test")
]
