from django.shortcuts import render

# Create your views here.


def welcome(request):
    context = {
        "content": "Лол",
    }

    return render(request, "welcomepage/welcome.html", context)
