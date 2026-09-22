from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Option, Poll, Vote

User = get_user_model()


def create_poll(author, question="Sinemaya mı gitsem?", options=("Sinema", "Restoran")):
    poll = Poll.objects.create(author=author, question=question)
    for order, text in enumerate(options):
        Option.objects.create(poll=poll, text=text, order=order)
    return poll


class PublicIdTests(TestCase):
    def test_public_id_is_random_and_not_sequential(self):
        author = User.objects.create_user(username="rastgele", email="rastgele@example.com", password="parola12345")
        poll_a = create_poll(author, question="Anket A")
        poll_b = create_poll(author, question="Anket B")

        self.assertEqual(len(poll_a.public_id), 12)
        self.assertNotEqual(poll_a.public_id, poll_b.public_id)
        self.assertFalse(poll_a.public_id.isdigit(), "public_id salt rakamlardan oluşmamalı")

        url = reverse("poll_detail", kwargs={"public_id": poll_a.public_id})
        self.assertEqual(url, f"/anket/{poll_a.public_id}/")


class VoteModelTests(TestCase):
    def test_unique_constraint_per_voter(self):
        author = User.objects.create_user(username="yazar", email="yazar@example.com", password="parola12345")
        poll = create_poll(author)
        option = poll.options.first()
        Vote.objects.create(poll=poll, option=option, voter_token="g:abc")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vote.objects.create(poll=poll, option=option, voter_token="g:abc")


class PollCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="olusturan", email="olusturan@example.com", password="parola12345")
        self.client.login(username="olusturan", password="parola12345")

    def _post(self, options, question="Bugün ne yesem?"):
        return self.client.post(reverse("poll_create"), {
            "question": question,
            "description": "",
            "option": options,
        })

    def test_valid_poll_created(self):
        response = self._post(["Pizza", "Lahmacun", "Mantı"])
        poll = Poll.objects.get(question="Bugün ne yesem?")
        self.assertRedirects(response, reverse("poll_detail", kwargs={"public_id": poll.public_id}))
        self.assertEqual(poll.options.count(), 3)

    def test_single_option_rejected(self):
        response = self._post(["Pizza"])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Poll.objects.filter(question="Bugün ne yesem?").exists())
        self.assertContains(response, "en az 2")

    def test_six_options_rejected(self):
        response = self._post(["A", "B", "C", "D", "E", "F"])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Poll.objects.filter(question="Bugün ne yesem?").exists())

    def test_duplicate_option_rejected(self):
        response = self._post(["Pizza", "pizza"])
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Poll.objects.filter(question="Bugün ne yesem?").exists())

    def test_blank_options_ignored(self):
        response = self._post(["Pizza", "", "Lahmacun", "  "])
        poll = Poll.objects.get(question="Bugün ne yesem?")
        self.assertRedirects(response, reverse("poll_detail", kwargs={"public_id": poll.public_id}))
        self.assertEqual(poll.options.count(), 2)

    def test_guest_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("poll_create"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('poll_create')}")


class VotingTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="anketsahibi", email="sahibi@example.com", password="parola12345")
        self.poll = create_poll(self.author)
        self.option = self.poll.options.first()

    def test_member_can_vote_once(self):
        member = User.objects.create_user(username="oyveren", email="oyveren@example.com", password="parola12345")
        self.client.login(username="oyveren", password="parola12345")

        response = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

        second = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(second.status_code, 409)

    def test_guest_can_vote_once_via_cookie(self):
        response = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertTrue(response.json()["ok"])

        second = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(second.status_code, 409)

    def test_vote_with_foreign_option_rejected(self):
        other_poll = create_poll(self.author, question="Başka anket", options=("A", "B"))
        foreign_option = other_poll.options.first()

        response = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": foreign_option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)

    def test_non_ajax_vote_redirects_to_detail(self):
        response = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
        )
        self.assertRedirects(response, reverse("poll_detail", kwargs={"public_id": self.poll.public_id}))


class PollDeleteTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="sahip", email="sahip@example.com", password="parola12345")
        self.poll = create_poll(self.author)

    def test_owner_can_delete(self):
        self.client.login(username="sahip", password="parola12345")
        response = self.client.post(reverse("poll_delete", kwargs={"public_id": self.poll.public_id}))
        self.assertRedirects(response, reverse("my_polls"))
        self.assertFalse(Poll.objects.filter(pk=self.poll.pk).exists())

    def test_non_owner_gets_404(self):
        User.objects.create_user(username="baskasi", email="baskasi@example.com", password="parola12345")
        self.client.login(username="baskasi", password="parola12345")
        response = self.client.post(reverse("poll_delete", kwargs={"public_id": self.poll.public_id}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Poll.objects.filter(pk=self.poll.pk).exists())


class EmailPrivacyTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="gizliyazar", email="gizli-eposta@example.com", password="parola12345"
        )
        self.poll = create_poll(self.author)
        self.option = self.poll.options.first()

    def test_email_not_in_poll_list(self):
        response = self.client.get(reverse("poll_list"))
        self.assertNotContains(response, "gizli-eposta@example.com")

    def test_email_not_in_poll_detail(self):
        response = self.client.get(reverse("poll_detail", kwargs={"public_id": self.poll.public_id}))
        self.assertNotContains(response, "gizli-eposta@example.com")

    def test_email_not_in_vote_json(self):
        response = self.client.post(
            reverse("vote", kwargs={"public_id": self.poll.public_id}),
            {"option_id": self.option.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertNotContains(response, "gizli-eposta@example.com")
