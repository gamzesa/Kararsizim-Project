import uuid

from django.conf import settings

VOTER_COOKIE_NAME = "kararsizim_voter"
VOTER_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 yıl


def get_or_create_guest_id(request):
    return request.COOKIES.get(VOTER_COOKIE_NAME) or str(uuid.uuid4())


def voter_token_for(request, guest_id):
    if request.user.is_authenticated:
        return f"u:{request.user.id}"
    return f"g:{guest_id}"


def set_voter_cookie_if_needed(request, response, guest_id):
    if not request.user.is_authenticated and VOTER_COOKIE_NAME not in request.COOKIES:
        response.set_cookie(
            VOTER_COOKIE_NAME,
            guest_id,
            max_age=VOTER_COOKIE_MAX_AGE,
            httponly=True,
            samesite="Lax",
            secure=not settings.DEBUG,
        )
    return response
