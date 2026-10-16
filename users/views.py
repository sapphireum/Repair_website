from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from users.forms import UserLoginForm
from django.contrib import auth, messages
from django.urls import reverse
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse("main:index"))

    else:
        form = UserLoginForm()

    context = {"title": "Авторизация", "form": form}

    return render(request, "users/login.html", context)


@login_required
def profile(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        user_profile = request.user.profile_img
        fir = request.user.first_name
        las = request.user.last_name
        join_date = request.user.date_joined

        context = {
            "username": username,
            "email": email,
            "img": user_profile,
            "fir": fir,
            "las": las,
            "date_joined": join_date,
        }
        return render(request, "users/profile.html", context)

    else:
        return HttpResponseRedirect(reverse("main:index"))


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("main:index"))
