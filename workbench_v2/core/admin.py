from django.contrib import admin
from .models import Source, Rule, Sentence, ReviewLog, Discussion, MemberProfile, Invitation, EvalRun, EvalResult


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["source_id", "name", "author", "year"]


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ["rule_id", "title", "category", "source", "is_active"]
    list_filter = ["category", "is_active", "source"]
    search_fields = ["rule_id", "title", "description"]


@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ["sentence_id", "rule", "sentence_type", "source", "status"]
    list_filter = ["sentence_type", "source", "status"]
    search_fields = ["sentence_id", "sentence"]


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ["sentence", "reviewer", "action", "review_number", "created_at"]
    list_filter = ["action", "review_number"]


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ["rule", "user", "created_at"]
    list_filter = ["rule"]


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "affiliation", "created_at"]
    list_filter = ["role"]
    search_fields = ["user__username", "affiliation"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["token", "email", "role", "invited_by", "is_used", "expires_at"]
    list_filter = ["role", "is_used"]
    search_fields = ["email"]


@admin.register(EvalRun)
class EvalRunAdmin(admin.ModelAdmin):
    list_display = ["id", "model_name", "run_by", "total_sentences", "detection_rate", "correction_accuracy", "created_at"]
    list_filter = ["model_name"]


@admin.register(EvalResult)
class EvalResultAdmin(admin.ModelAdmin):
    list_display = ["id", "eval_run", "sentence", "outcome"]
    list_filter = ["outcome"]
