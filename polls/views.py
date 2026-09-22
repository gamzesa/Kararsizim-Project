from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PollCreateForm, clean_options
from .models import Option, Poll, Vote
from .utils import get_or_create_guest_id, set_voter_cookie_if_needed, voter_token_for


def poll_list(request):
    polls = (
        Poll.objects.select_related("author")
        .prefetch_related("options")
        .annotate(total_votes=Count("votes"))
        .order_by("-created_at")
    )
    paginator = Paginator(polls, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "polls/poll_list.html", {"page_obj": page_obj})


def _poll_results(poll, options):
    total_votes = sum(option.vote_count for option in options)
    results = []
    for option in options:
        percent = round(option.vote_count / total_votes * 100, 1) if total_votes else 0
        results.append({"option": option, "votes": option.vote_count, "percent": percent})
    return total_votes, results


def poll_detail(request, public_id):
    poll = get_object_or_404(Poll.objects.select_related("author"), public_id=public_id)
    options = list(poll.options.annotate(vote_count=Count("votes")))

    guest_id = get_or_create_guest_id(request)
    voter_token = voter_token_for(request, guest_id)
    user_vote = Vote.objects.filter(poll=poll, voter_token=voter_token).first()

    is_owner = request.user.is_authenticated and poll.author_id == request.user.id
    show_results = user_vote is not None or is_owner
    total_votes, results = _poll_results(poll, options)

    response = render(request, "polls/poll_detail.html", {
        "poll": poll,
        "options": options,
        "show_results": show_results,
        "results": results if show_results else None,
        "total_votes": total_votes,
        "voted_option_id": user_vote.option_id if user_vote else None,
        "is_owner": is_owner,
    })
    return set_voter_cookie_if_needed(request, response, guest_id)


@login_required
def poll_create(request):
    if request.method == "POST":
        form = PollCreateForm(request.POST)
        options, option_error = clean_options(request.POST.getlist("option"))

        if form.is_valid() and option_error is None:
            with transaction.atomic():
                poll = Poll.objects.create(
                    author=request.user,
                    question=form.cleaned_data["question"],
                    description=form.cleaned_data["description"],
                )
                Option.objects.bulk_create([
                    Option(poll=poll, text=text, order=order)
                    for order, text in enumerate(options)
                ])
            messages.success(request, "Anketin oluşturuldu!")
            return redirect("poll_detail", public_id=poll.public_id)
    else:
        form = PollCreateForm()
        option_error = None

    return render(request, "polls/poll_create.html", {
        "form": form,
        "option_error": option_error,
        "submitted_options": request.POST.getlist("option") if request.method == "POST" else ["", ""],
    })


@require_POST
@login_required
def poll_delete(request, public_id):
    poll = get_object_or_404(Poll, public_id=public_id, author=request.user)
    poll.delete()
    messages.success(request, "Anket silindi.")
    return redirect("my_polls")


@login_required
def my_polls(request):
    polls = (
        request.user.polls.prefetch_related("options")
        .annotate(total_votes=Count("votes"))
        .order_by("-created_at")
    )
    return render(request, "polls/my_polls.html", {"polls": polls})


@require_POST
def vote(request, public_id):
    poll = get_object_or_404(Poll, public_id=public_id)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    guest_id = get_or_create_guest_id(request)
    voter_token = voter_token_for(request, guest_id)

    option_id = request.POST.get("option_id")
    option = Option.objects.filter(pk=option_id, poll=poll).first()
    if option is None:
        if is_ajax:
            return JsonResponse({"ok": False, "error": "Geçersiz seçenek."}, status=400)
        messages.error(request, "Geçersiz seçenek.")
        return redirect("poll_detail", public_id=poll.public_id)

    try:
        with transaction.atomic():
            Vote.objects.create(
                poll=poll,
                option=option,
                user=request.user if request.user.is_authenticated else None,
                voter_token=voter_token,
            )
    except IntegrityError:
        if is_ajax:
            response = JsonResponse({"ok": False, "error": "Bu ankete zaten oy verdin."}, status=409)
            return set_voter_cookie_if_needed(request, response, guest_id)
        messages.error(request, "Bu ankete zaten oy verdin.")
        return redirect("poll_detail", public_id=poll.public_id)

    options = list(poll.options.annotate(vote_count=Count("votes")))
    total_votes, results = _poll_results(poll, options)

    if is_ajax:
        response = JsonResponse({
            "ok": True,
            "total_votes": total_votes,
            "voted_option_id": option.id,
            "results": [
                {"option_id": r["option"].id, "text": r["option"].text, "votes": r["votes"], "percent": r["percent"]}
                for r in results
            ],
        })
    else:
        response = redirect("poll_detail", public_id=poll.public_id)

    return set_voter_cookie_if_needed(request, response, guest_id)
