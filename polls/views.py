from django.shortcuts import render


def poll_list(request):
    return render(request, "polls/poll_list.html")
