from django.contrib import admin

from .models import Option, Poll, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "created_at")
    inlines = [OptionInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("poll", "option", "voter_token", "created_at")
    readonly_fields = ("poll", "option", "user", "voter_token", "created_at")

    def has_add_permission(self, request):
        return False
