from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string

# l, 1, I, O, 0 gibi karışabilecek karakterler çıkarıldı.
PUBLIC_ID_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"
PUBLIC_ID_LENGTH = 12


def generate_public_id():
    while True:
        candidate = get_random_string(PUBLIC_ID_LENGTH, allowed_chars=PUBLIC_ID_ALPHABET)
        if not Poll.objects.filter(public_id=candidate).exists():
            return candidate


class Poll(models.Model):
    public_id = models.CharField(max_length=PUBLIC_ID_LENGTH, unique=True, editable=False, default=generate_public_id)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    voter_token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "voter_token"], name="one_vote_per_voter_per_poll"),
        ]
