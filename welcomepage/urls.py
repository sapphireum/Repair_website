from django.urls import path
from welcomepage import views

app_name = "welcome"

urlpatterns = [
    path("", views.welcome, name="welcome"),
    # path("zero/", views.zero, name="zero"),
    # path("postorder/", views.postorder, name="postorder"),
    # path("postupdate/", views.postupdate, name="postorder"),
]