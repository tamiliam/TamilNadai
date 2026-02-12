"""Data models for TamilNadai Workbench v2."""

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Source(models.Model):
    """A publication or book that rules come from."""

    source_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True, default="")
    year = models.IntegerField(null=True, blank=True)
    url = models.URLField(max_length=500, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.year})" if self.year else self.name


class Rule(models.Model):
    """A Tamil grammar rule from the source material."""

    rule_id = models.CharField(max_length=20, primary_key=True)
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=200, blank=True, default="")
    subtitle = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    example_1 = models.CharField(max_length=200, blank=True, default="")
    example_2 = models.CharField(max_length=200, blank=True, default="")
    source = models.ForeignKey(
        Source, on_delete=models.SET_NULL, null=True, blank=True, related_name="rules"
    )
    source_page = models.IntegerField(null=True, blank=True)
    source_ref = models.CharField(max_length=200, blank=True, default="")
    source_url = models.URLField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rule_id"]

    def __str__(self):
        return f"{self.rule_id} — {self.title}"

    @property
    def correct_sentences(self):
        return self.sentences.filter(sentence_type="correct")

    @property
    def wrong_sentences(self):
        return self.sentences.filter(sentence_type="wrong")

    @property
    def accepted_count(self):
        return self.sentences.filter(status="accepted").count()

    @property
    def pending_count(self):
        return self.sentences.filter(status__in=["pending", "review_1_done"]).count()

    @property
    def category_short(self):
        mapping = {
            "இலக்கண அமைப்பில் சொற்கள்": "Grammar Structure",
            "தனிச் சொற்களை எழுதும் முறை": "Individual Words",
            "சந்தி": "Sandhi",
        }
        return mapping.get(self.category, self.category)

    @property
    def category_color(self):
        mapping = {
            "இலக்கண அமைப்பில் சொற்கள்": "blue",
            "தனிச் சொற்களை எழுதும் முறை": "green",
            "சந்தி": "purple",
        }
        return mapping.get(self.category, "gray")


class Sentence(models.Model):
    """An example sentence linked to a rule."""

    TYPE_CHOICES = [("correct", "Correct"), ("wrong", "Wrong")]
    SOURCE_CHOICES = [("book", "Book"), ("ai", "AI"), ("manual", "Manual"), ("proposed", "Proposed")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("review_1_done", "Review 1 Done"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    sentence_id = models.CharField(max_length=20, primary_key=True)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="sentences")
    sentence = models.TextField()
    sentence_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="book")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    review_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="sentences_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sentence_id"]

    def __str__(self):
        return f"{self.sentence_id}: {self.sentence[:50]}"

    @property
    def source_badge_class(self):
        return {
            "book": "bg-gray-100 text-gray-700",
            "ai": "bg-purple-100 text-purple-700",
            "manual": "bg-blue-100 text-blue-700",
        }.get(self.source, "bg-gray-100")

    @property
    def status_badge_class(self):
        return {
            "pending": "bg-orange-100 text-orange-700",
            "review_1_done": "bg-yellow-100 text-yellow-700",
            "accepted": "bg-green-100 text-green-700",
            "rejected": "bg-red-100 text-red-700",
        }.get(self.status, "bg-gray-100")


class ReviewLog(models.Model):
    """Immutable audit trail of review actions.
    Reviewers can only accept or reject with a comment. No editing."""

    ACTION_CHOICES = [("accept", "Accept"), ("reject", "Reject")]

    sentence = models.ForeignKey(
        Sentence, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_logs"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True, default="")
    review_number = models.IntegerField()  # 1 or 2
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reviewer} {self.action}ed {self.sentence_id} (R{self.review_number})"


class Discussion(models.Model):
    """Per-rule threaded discussion."""

    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="discussions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussions"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} on {self.rule_id}: {self.message[:40]}"


class MemberProfile(models.Model):
    """Extended profile for workbench members with role-based permissions."""

    ROLE_CHOICES = [("admin", "Admin"), ("reviewer", "Reviewer"), ("member", "Member")]
    ROLE_LEVELS = {"admin": 3, "reviewer": 2, "member": 1}

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    affiliation = models.CharField(max_length=200, blank=True, default="")
    avatar = models.TextField(blank=True, default="")  # base64 data URI
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_memberprofile"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def has_role(self, min_role: str) -> bool:
        """Check if user has at least the given role level."""
        return self.ROLE_LEVELS.get(self.role, 0) >= self.ROLE_LEVELS.get(min_role, 0)

    def save(self, *args, **kwargs):
        # Keep User.is_staff in sync with admin role
        if self.user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.filter(pk=self.user_id).update(is_staff=(self.role == "admin"))
        super().save(*args, **kwargs)


class Invitation(models.Model):
    """Token-based invitation for new members."""

    ROLE_CHOICES = [("admin", "Admin"), ("reviewer", "Reviewer"), ("member", "Member")]

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(blank=True, default="")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "core_invitation"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite {self.email or '(no email)'} as {self.role} by {self.invited_by}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at


class EvalRun(models.Model):
    """A single evaluation run testing an LLM against the sentence dataset."""

    MODEL_CHOICES = [
        ("gemini-2.0-flash", "Gemini 2.0 Flash"),
        ("claude-sonnet-4-5", "Claude Sonnet 4.5"),
        ("gpt-4o", "GPT-4o"),
    ]
    STATUS_FILTER_CHOICES = [("all", "All Sentences"), ("accepted", "Accepted Only")]
    RUN_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    status = models.CharField(max_length=20, choices=RUN_STATUS_CHOICES, default="pending")
    run_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eval_runs"
    )
    category_filter = models.CharField(max_length=100, blank=True, default="")
    status_filter = models.CharField(
        max_length=20, choices=STATUS_FILTER_CHOICES, default="all"
    )
    total_sentences = models.IntegerField(default=0)
    detection_rate = models.FloatField(null=True, blank=True)
    correction_accuracy = models.FloatField(null=True, blank=True)
    false_positive_rate = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Eval {self.id}: {self.get_model_name_display()} ({self.created_at:%Y-%m-%d %H:%M})"

    @property
    def is_complete(self):
        return self.status == "completed"

    @property
    def is_running(self):
        return self.status == "running"

    @property
    def is_failed(self):
        return self.status == "failed"

    @property
    def preservation_rate(self):
        if self.false_positive_rate is not None:
            return round(100 - self.false_positive_rate, 1)
        return None


class EvalResult(models.Model):
    """Per-sentence result from an evaluation run."""

    OUTCOME_CHOICES = [
        ("true_positive", "True Positive"),
        ("partial", "Partial"),
        ("false_negative", "False Negative"),
        ("true_negative", "True Negative"),
        ("false_positive", "False Positive"),
        ("error", "Error"),
    ]

    eval_run = models.ForeignKey(
        EvalRun, on_delete=models.CASCADE, related_name="results"
    )
    sentence = models.ForeignKey(
        Sentence, on_delete=models.CASCADE, related_name="eval_results"
    )
    model_response = models.TextField(blank=True, default="")
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sentence__sentence_id"]

    def __str__(self):
        return f"{self.sentence_id}: {self.outcome}"

    @property
    def outcome_badge_class(self):
        return {
            "true_positive": "bg-palmgreen-bg text-palmgreen",
            "partial": "bg-leaf-200 text-stylus-dark",
            "false_negative": "bg-terracotta-bg text-terracotta",
            "true_negative": "bg-palmgreen-bg text-palmgreen",
            "false_positive": "bg-terracotta-bg text-terracotta",
            "error": "bg-leaf-300 text-etch-lighter",
        }.get(self.outcome, "bg-leaf-200 text-etch-lighter")
