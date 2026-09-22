from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("poll_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            messages.success(request, f"Hoş geldin, {user.username}!")
            return redirect(request.GET.get("next") or "poll_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect("poll_list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["identifier"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                auth_login(request, user)
                return redirect(request.POST.get("next") or "poll_list")
            form.add_error(None, "E-posta/kullanıcı adı veya parola hatalı.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {
        "form": form,
        "next": request.GET.get("next", ""),
    })


@require_POST
@login_required
def logout(request):
    auth_logout(request)
    return redirect("poll_list")
