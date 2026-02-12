"""Views for TamilNadai Workbench v2."""

import csv
import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.expressions import RawSQL
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone

# Natural sort for rule IDs (1.2.1 before 1.10.1)
_USING_POSTGRES = "sqlite3" not in settings.DATABASES["default"]["ENGINE"]
RULE_NATURAL_ORDER = (
    (RawSQL("string_to_array(regexp_replace(core_rule.rule_id, '[^0-9.]', '', 'g'), '.')::int[]", []), "rule_id")
    if _USING_POSTGRES
    else ("rule_id",)
)

from .models import Source, Rule, Sentence, ReviewLog, Discussion, MemberProfile, Invitation, EvalRun, EvalResult
from .forms import (
    RuleForm, SentenceForm, ReviewForm, DiscussionForm,
    ProfileForm, InvitationForm, AdminInvitationForm, RegistrationForm,
)
from .services import suggest_sentence
from .decorators import require_role


# --- Auth ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "dashboard"))
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# --- Dashboard ---

@login_required
def dashboard(request):
    rules = Rule.objects.filter(is_active=True)
    total_rules = rules.count()
    total_sentences = Sentence.objects.count()
    accepted = Sentence.objects.filter(status="accepted").count()
    pending = Sentence.objects.filter(status__in=["pending", "review_1_done"]).count()

    # Per-category stats
    categories = []
    for cat_name, cat_short in [
        ("இலக்கண அமைப்பில் சொற்கள்", "Grammar Structure"),
        ("தனிச் சொற்களை எழுதும் முறை", "Individual Words"),
        ("சந்தி", "Sandhi"),
    ]:
        cat_rules = rules.filter(category=cat_name)
        cat_count = cat_rules.count()
        cat_sentences = Sentence.objects.filter(rule__category=cat_name)
        cat_accepted = cat_sentences.filter(status="accepted").count()
        cat_total = cat_sentences.count()
        pct = int(cat_accepted / cat_total * 100) if cat_total > 0 else 0
        categories.append({
            "name": cat_name,
            "short": cat_short,
            "rule_count": cat_count,
            "sentence_count": cat_total,
            "accepted": cat_accepted,
            "pct": pct,
        })

    # Recent activity
    recent = ReviewLog.objects.select_related("sentence", "reviewer")[:20]

    return render(request, "dashboard.html", {
        "total_rules": total_rules,
        "total_sentences": total_sentences,
        "accepted": accepted,
        "pending": pending,
        "categories": categories,
        "recent": recent,
    })


# --- Rule List ---

@login_required
def rule_list(request):
    qs = Rule.objects.filter(is_active=True).select_related("source")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(rule_id__icontains=q)
            | Q(title__icontains=q)
            | Q(description__icontains=q)
        )

    # Filters
    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(category=category)

    source_filter = request.GET.get("source", "")
    if source_filter:
        qs = qs.filter(source_id=source_filter)

    status_filter = request.GET.get("status", "")
    if status_filter == "complete":
        qs = qs.annotate(
            pending_ct=Count("sentences", filter=Q(sentences__status__in=["pending", "review_1_done"]))
        ).filter(pending_ct=0)
    elif status_filter == "in_progress":
        qs = qs.annotate(
            accepted_ct=Count("sentences", filter=Q(sentences__status="accepted")),
            total_ct=Count("sentences"),
        ).filter(total_ct__gt=0, accepted_ct__lt=Count("sentences"))
    elif status_filter == "empty":
        qs = qs.annotate(total_ct=Count("sentences")).filter(total_ct=0)

    # Annotate counts
    qs = qs.annotate(
        correct_ct=Count("sentences", filter=Q(sentences__sentence_type="correct")),
        wrong_ct=Count("sentences", filter=Q(sentences__sentence_type="wrong")),
        total_ct=Count("sentences"),
        accepted_ct=Count("sentences", filter=Q(sentences__status="accepted")),
    ).order_by(*RULE_NATURAL_ORDER)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))

    sources = Source.objects.all()

    return render(request, "rule_list.html", {
        "page": page,
        "q": q,
        "category": category,
        "source_filter": source_filter,
        "status_filter": status_filter,
        "sources": sources,
        "total_count": paginator.count,
    })


# --- Rule Detail ---

@login_required
def rule_detail(request, rule_id):
    rule = get_object_or_404(Rule, rule_id=rule_id)
    correct = rule.sentences.filter(sentence_type="correct").select_related("created_by").order_by("sentence_id")
    wrong = rule.sentences.filter(sentence_type="wrong").select_related("created_by").order_by("sentence_id")

    # Get review info for each sentence
    for s in list(correct) + list(wrong):
        s.review_list = s.reviews.select_related("reviewer").order_by("review_number")
        s.user_already_reviewed = s.reviews.filter(reviewer=request.user).exists()

    discussions = rule.discussions.select_related("user").order_by("created_at")
    recent_activity = ReviewLog.objects.filter(
        sentence__rule=rule
    ).select_related("sentence", "reviewer")[:10]

    # Prev/next rule navigation
    all_ids = list(
        Rule.objects.filter(is_active=True)
        .order_by(*RULE_NATURAL_ORDER)
        .values_list("rule_id", flat=True)
    )
    try:
        idx = all_ids.index(rule_id)
    except ValueError:
        idx = -1
    prev_rule_id = all_ids[idx - 1] if idx > 0 else None
    next_rule_id = all_ids[idx + 1] if idx < len(all_ids) - 1 else None

    return render(request, "rule_detail.html", {
        "rule": rule,
        "correct": correct,
        "wrong": wrong,
        "discussions": discussions,
        "recent_activity": recent_activity,
        "sentence_form": SentenceForm(),
        "review_form": ReviewForm(),
        "discussion_form": DiscussionForm(),
        "prev_rule_id": prev_rule_id,
        "next_rule_id": next_rule_id,
    })


# --- Review a sentence (reviewer or above) ---

@require_role("reviewer")
def review_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, sentence_id=sentence_id)

    if request.method != "POST":
        return redirect("rule_detail", rule_id=sentence.rule_id)

    if sentence.reviews.filter(reviewer=request.user).exists():
        messages.warning(request, "You have already reviewed this sentence.")
        return redirect("rule_detail", rule_id=sentence.rule_id)

    action = request.POST.get("action", "")
    comment = request.POST.get("comment", "")

    if action not in ("accept", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("rule_detail", rule_id=sentence.rule_id)

    existing_reviews = sentence.reviews.count()
    if existing_reviews >= 2:
        messages.warning(request, "This sentence has already been fully reviewed.")
        return redirect("rule_detail", rule_id=sentence.rule_id)

    review_number = existing_reviews + 1

    ReviewLog.objects.create(
        sentence=sentence,
        reviewer=request.user,
        action=action,
        comment=comment,
        review_number=review_number,
    )

    sentence.review_count = review_number
    if review_number == 1:
        sentence.status = "review_1_done"
    elif review_number == 2:
        first_review = sentence.reviews.filter(review_number=1).first()
        if first_review and first_review.action == "accept" and action == "accept":
            sentence.status = "accepted"
        else:
            sentence.status = "rejected"
    sentence.save()

    messages.success(request, f"Review {review_number} recorded for {sentence_id}.")
    return redirect("rule_detail", rule_id=sentence.rule_id)


# --- Add sentence (all logged-in users; admin=manual, others=proposed) ---

@login_required
def add_sentence(request, rule_id):
    rule = get_object_or_404(Rule, rule_id=rule_id)

    if request.method == "POST":
        form = SentenceForm(request.POST)
        if form.is_valid():
            last = Sentence.objects.order_by("-sentence_id").first()
            if last:
                num = int(last.sentence_id.split("-")[1]) + 1
            else:
                num = 1
            sid = f"SEN-{num:05d}"

            profile = getattr(request.user, "profile", None)
            is_admin_user = profile and profile.has_role("admin")
            source = "manual" if is_admin_user else "proposed"

            Sentence.objects.create(
                sentence_id=sid,
                rule=rule,
                sentence=form.cleaned_data["sentence"],
                sentence_type=form.cleaned_data["sentence_type"],
                source=source,
                status="pending",
                created_by=request.user,
            )
            label = "Added" if is_admin_user else "Proposed"
            messages.success(request, f"{label} {sid}.")

    return redirect("rule_detail", rule_id=rule_id)


# --- Edit sentence (admin only) ---

@require_role("admin")
def edit_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, sentence_id=sentence_id)

    if request.method == "POST":
        new_text = request.POST.get("sentence", "").strip()
        if new_text:
            sentence.sentence = new_text
            sentence.save()
            messages.success(request, f"Updated {sentence_id}.")

    return redirect("rule_detail", rule_id=sentence.rule_id)


# --- Delete sentence (admin only) ---

@require_role("admin")
def delete_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, sentence_id=sentence_id)
    rule_id = sentence.rule_id

    if request.method == "POST":
        sentence.delete()
        messages.success(request, f"Deleted {sentence_id}.")

    return redirect("rule_detail", rule_id=rule_id)


# --- Add/Edit Rule (admin only) ---

@require_role("admin")
def rule_add(request):
    if request.method == "POST":
        form = RuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            if rule.source and rule.source_page:
                rule.source_ref = f"{rule.source.name}, ப.{rule.source_page}"
                if rule.source.url:
                    rule.source_url = f"{rule.source.url}&pno={rule.source_page}"
            rule.save()
            messages.success(request, f"Rule {rule.rule_id} created.")
            return redirect("rule_detail", rule_id=rule.rule_id)
    else:
        form = RuleForm()

    return render(request, "rule_form.html", {"form": form, "editing": False})


@require_role("admin")
def rule_edit(request, rule_id):
    rule = get_object_or_404(Rule, rule_id=rule_id)

    if request.method == "POST":
        form = RuleForm(request.POST, instance=rule)
        if form.is_valid():
            rule = form.save(commit=False)
            if rule.source and rule.source_page:
                rule.source_ref = f"{rule.source.name}, ப.{rule.source_page}"
                if rule.source.url:
                    rule.source_url = f"{rule.source.url}&pno={rule.source_page}"
            rule.save()
            messages.success(request, f"Rule {rule.rule_id} updated.")
            return redirect("rule_detail", rule_id=rule.rule_id)
    else:
        form = RuleForm(instance=rule)

    return render(request, "rule_form.html", {"form": form, "editing": True, "rule": rule})


@require_role("admin")
def rule_deactivate(request, rule_id):
    rule = get_object_or_404(Rule, rule_id=rule_id)
    if request.method == "POST":
        rule.is_active = False
        rule.save()
        messages.success(request, f"Rule {rule_id} deactivated.")
    return redirect("rule_list")


# --- Discussion ---

@login_required
def add_discussion(request, rule_id):
    rule = get_object_or_404(Rule, rule_id=rule_id)

    if request.method == "POST":
        form = DiscussionForm(request.POST)
        if form.is_valid():
            Discussion.objects.create(
                rule=rule,
                user=request.user,
                message=form.cleaned_data["message"],
            )
            messages.success(request, "Comment posted.")

    return redirect("rule_detail", rule_id=rule_id)


@login_required
def delete_discussion(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    rule_id = discussion.rule_id

    if request.method == "POST":
        profile = getattr(request.user, "profile", None)
        is_admin_user = profile and profile.has_role("admin")
        if discussion.user == request.user or is_admin_user:
            discussion.delete()
            messages.success(request, "Comment deleted.")
        else:
            messages.error(request, "You can only delete your own comments.")

    return redirect("rule_detail", rule_id=rule_id)


# --- AI Suggest (returns JSON, user edits before submitting) ---

@login_required
def ai_suggest(request, rule_id):
    """AJAX endpoint: return one AI-suggested sentence for the user to edit."""
    from django.http import JsonResponse

    rule = get_object_or_404(Rule, rule_id=rule_id)
    sentence_type = request.GET.get("type", "correct")
    if sentence_type not in ("correct", "wrong"):
        return JsonResponse({"error": "Invalid type"}, status=400)

    text = suggest_sentence(rule, sentence_type)
    if text is None:
        return JsonResponse({"error": "AI generation failed"}, status=500)

    return JsonResponse({"sentence": text})


# --- Review Queue ---

@login_required
def review_queue(request):
    qs = Sentence.objects.filter(
        status__in=["pending", "review_1_done"]
    ).select_related("rule")

    status_filter = request.GET.get("status", "")
    if status_filter == "pending":
        qs = qs.filter(status="pending")
    elif status_filter == "review_1_done":
        qs = qs.filter(status="review_1_done")

    category = request.GET.get("category", "")
    if category:
        qs = qs.filter(rule__category=category)

    sentence_type = request.GET.get("type", "")
    if sentence_type:
        qs = qs.filter(sentence_type=sentence_type)

    source_filter = request.GET.get("source", "")
    if source_filter:
        qs = qs.filter(source=source_filter)

    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "review_queue.html", {
        "page": page,
        "status_filter": status_filter,
        "category": category,
        "sentence_type": sentence_type,
        "source_filter": source_filter,
        "total_count": paginator.count,
    })


# --- Review Log ---

@login_required
def review_log(request):
    qs = ReviewLog.objects.select_related("sentence", "reviewer")

    reviewer_filter = request.GET.get("reviewer", "")
    if reviewer_filter:
        qs = qs.filter(reviewer__username=reviewer_filter)

    action_filter = request.GET.get("action", "")
    if action_filter:
        qs = qs.filter(action=action_filter)

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "review_log.html", {
        "page": page,
        "reviewer_filter": reviewer_filter,
        "action_filter": action_filter,
        "total_count": paginator.count,
    })


# --- Profile ---

@login_required
def profile_view(request):
    profile, _ = MemberProfile.objects.get_or_create(
        user=request.user, defaults={"role": "admin" if request.user.is_staff else "member"}
    )

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            profile.affiliation = form.cleaned_data["affiliation"]
            profile.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "affiliation": profile.affiliation,
        })

    return render(request, "profile.html", {"form": form, "profile": profile})


@login_required
def change_password(request):
    if request.method == "POST":
        current = request.POST.get("current_password", "")
        new_pw = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")

        if not request.user.check_password(current):
            messages.error(request, "Current password is incorrect.")
        elif new_pw != confirm:
            messages.error(request, "New passwords do not match.")
        elif len(new_pw) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        else:
            request.user.set_password(new_pw)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully.")

    return redirect("profile")


@login_required
def upload_avatar(request):
    """Handle avatar upload: resize/crop to 200x200, store as base64."""
    if request.method != "POST" or "avatar" not in request.FILES:
        return redirect("profile")

    import base64
    from io import BytesIO
    from PIL import Image

    file = request.FILES["avatar"]

    # Validate size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        messages.error(request, "Image too large. Maximum 5 MB.")
        return redirect("profile")

    try:
        img = Image.open(file)
        img = img.convert("RGB")

        # Crop to square (center crop)
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))

        # Resize to 200x200
        img = img.resize((200, 200), Image.LANCZOS)

        # Encode to base64 JPEG
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")

        profile, _ = MemberProfile.objects.get_or_create(
            user=request.user,
            defaults={"role": "admin" if request.user.is_staff else "member"},
        )
        profile.avatar = f"data:image/jpeg;base64,{b64}"
        profile.save()
        messages.success(request, "Avatar updated.")
    except Exception:
        messages.error(request, "Could not process image. Try a different file.")

    return redirect("profile")


# --- Members (admin only) ---

@require_role("admin")
def members_list(request):
    members = User.objects.filter(is_active=True).select_related("profile").order_by("username")
    return render(request, "members.html", {"members": members})


@require_role("admin")
def change_role(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot change your own role.")
        return redirect("members_list")

    if request.method == "POST":
        new_role = request.POST.get("role", "")
        if new_role in ("admin", "reviewer", "member"):
            profile, _ = MemberProfile.objects.get_or_create(
                user=target_user, defaults={"role": new_role}
            )
            profile.role = new_role
            profile.save()
            messages.success(request, f"{target_user.username} is now {new_role}.")

    return redirect("members_list")


@require_role("admin")
def remove_member(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot remove yourself.")
        return redirect("members_list")

    if request.method == "POST":
        target_user.is_active = False
        target_user.save()
        messages.success(request, f"{target_user.username} has been deactivated.")

    return redirect("members_list")


# --- Invitation ---

@login_required
def invite_member(request):
    profile = getattr(request.user, "profile", None)
    is_admin_user = profile and profile.has_role("admin")

    if request.method == "POST":
        if is_admin_user:
            form = AdminInvitationForm(request.POST)
        else:
            form = InvitationForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get("role", "member")
            if not is_admin_user:
                role = "member"

            Invitation.objects.create(
                email=form.cleaned_data.get("email", ""),
                invited_by=request.user,
                role=role,
                expires_at=timezone.now() + timedelta(days=7),
            )
            messages.success(request, "Invitation created. Share the link below with the invitee.")
            return redirect("invite")
    else:
        form = AdminInvitationForm() if is_admin_user else InvitationForm()

    now = timezone.now()
    my_invitations = Invitation.objects.filter(invited_by=request.user).order_by("-created_at")
    active_invitations = [i for i in my_invitations if not i.is_used and now < i.expires_at]
    past_invitations = [i for i in my_invitations if i.is_used or now >= i.expires_at][:10]

    return render(request, "invite.html", {
        "form": form,
        "active_invitations": active_invitations,
        "past_invitations": past_invitations,
    })


# --- Registration (public, requires valid invitation token) ---

def register_view(request, token):
    invitation = get_object_or_404(Invitation, token=token)

    if not invitation.is_valid:
        messages.error(request, "This invitation has expired or already been used.")
        return redirect("login")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data.get("first_name", ""),
                last_name=form.cleaned_data.get("last_name", ""),
                is_staff=(invitation.role == "admin"),
            )
            MemberProfile.objects.create(
                user=user,
                role=invitation.role,
                affiliation=form.cleaned_data.get("affiliation", ""),
            )
            invitation.is_used = True
            invitation.save()

            login(request, user)
            messages.success(request, f"Welcome! You've joined as {invitation.get_role_display()}.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()

    return render(request, "register.html", {
        "form": form,
        "invitation": invitation,
    })


# --- Static pages (public) ---

def about_view(request):
    return render(request, "about.html")


def privacy_view(request):
    return render(request, "privacy.html")


def terms_view(request):
    return render(request, "terms.html")


def cookies_view(request):
    return render(request, "cookies.html")


# --- Evaluation ---

@require_role("admin")
def evaluate_view(request):
    from .eval_service import get_available_models
    runs = EvalRun.objects.select_related("run_by")[:20]
    models_list = get_available_models()
    has_running = EvalRun.objects.filter(status="running").exists()
    return render(request, "evaluate.html", {
        "runs": runs,
        "models_list": models_list,
        "has_running": has_running,
    })


@require_role("admin")
def run_evaluation_view(request):
    from .eval_service import run_evaluation as do_eval, get_available_models

    if request.method != "POST":
        return redirect("evaluate")

    model_name = request.POST.get("model_name", "")
    category_filter = request.POST.get("category_filter", "")
    status_filter = request.POST.get("status_filter", "all")

    # Validate model
    available = {m["id"] for m in get_available_models() if m["available"]}
    if model_name not in available:
        messages.error(request, "Selected model is not available (missing API key).")
        return redirect("evaluate")

    # Build sentence queryset
    qs = Sentence.objects.select_related("rule")
    if category_filter:
        qs = qs.filter(rule__category=category_filter)
    if status_filter == "accepted":
        qs = qs.filter(status="accepted")

    if not qs.exists():
        messages.warning(request, "No sentences match the selected filters.")
        return redirect("evaluate")

    # Create the run
    eval_run = EvalRun.objects.create(
        model_name=model_name,
        run_by=request.user,
        category_filter=category_filter,
        status_filter=status_filter,
    )

    # Materialise the queryset before spawning the thread so it doesn't
    # depend on the request context. list() forces DB evaluation now.
    sentence_list = list(qs)

    # Run evaluation in a background thread
    import threading
    thread = threading.Thread(
        target=do_eval,
        args=(eval_run, sentence_list),
        daemon=True,
    )
    thread.start()

    messages.info(
        request,
        f"Evaluation started: {len(sentence_list)} sentences with "
        f"{eval_run.get_model_name_display()}. This page will auto-refresh."
    )
    return redirect("evaluate")


@require_role("admin")
def eval_detail(request, run_id):
    eval_run = get_object_or_404(EvalRun, id=run_id)
    results = eval_run.results.select_related("sentence", "sentence__rule")

    # Filters
    outcome_filter = request.GET.get("outcome", "")
    if outcome_filter:
        results = results.filter(outcome=outcome_filter)

    category_filter = request.GET.get("category", "")
    if category_filter:
        results = results.filter(sentence__rule__category=category_filter)

    # Per-category breakdown
    all_results = eval_run.results.select_related("sentence", "sentence__rule")
    categories = []
    for cat_name, cat_short in [
        ("இலக்கண அமைப்பில் சொற்கள்", "Grammar Structure"),
        ("தனிச் சொற்களை எழுதும் முறை", "Individual Words"),
        ("சந்தி", "Sandhi"),
    ]:
        cat_results = [r for r in all_results if r.sentence.rule.category == cat_name]
        if not cat_results:
            continue

        wrong = [r for r in cat_results if r.sentence.sentence_type == "wrong"]
        correct = [r for r in cat_results if r.sentence.sentence_type == "correct"]

        detection = 0
        accuracy = 0
        fp_rate = 0

        if wrong:
            detected = sum(1 for r in wrong if r.outcome != "false_negative")
            detection = round(detected / len(wrong) * 100, 1)
            correct_fixes = sum(1 for r in wrong if r.outcome == "true_positive")
            accuracy = round(correct_fixes / len(wrong) * 100, 1)
        if correct:
            false_pos = sum(1 for r in correct if r.outcome == "false_positive")
            fp_rate = round(false_pos / len(correct) * 100, 1)

        categories.append({
            "name": cat_name,
            "short": cat_short,
            "total": len(cat_results),
            "detection_rate": detection,
            "correction_accuracy": accuracy,
            "preservation_rate": round(100 - fp_rate, 1),
        })

    paginator = Paginator(results, 50)
    page = paginator.get_page(request.GET.get("page", 1))

    return render(request, "eval_detail.html", {
        "eval_run": eval_run,
        "page": page,
        "categories": categories,
        "outcome_filter": outcome_filter,
        "category_filter": category_filter,
    })


# --- Exports (any logged-in member) ---

CATEGORY_SHORT = {
    "இலக்கண அமைப்பில் சொற்கள்": "Grammar Structure",
    "தனிச் சொற்களை எழுதும் முறை": "Individual Words",
    "சந்தி": "Sandhi",
}


@login_required
def exports_page(request):
    """Exports landing page — dataset + eval runs available for download."""
    rule_count = Rule.objects.filter(is_active=True).count()
    sentence_count = Sentence.objects.count()
    accepted_count = Sentence.objects.filter(status="accepted").count()
    eval_runs = EvalRun.objects.select_related("run_by").order_by("-created_at")[:20]

    return render(request, "exports.html", {
        "rule_count": rule_count,
        "sentence_count": sentence_count,
        "accepted_count": accepted_count,
        "eval_runs": eval_runs,
    })


@login_required
def export_dataset(request, fmt):
    """Download all rules + sentences as CSV or JSON."""
    if fmt not in ("csv", "json"):
        return HttpResponse("Invalid format. Use .csv or .json", status=400)

    rules = (
        Rule.objects.filter(is_active=True)
        .select_related("source")
        .prefetch_related("sentences", "sentences__created_by")
        .order_by(*RULE_NATURAL_ORDER)
    )
    today = timezone.now().strftime("%Y-%m-%d")

    if fmt == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="tamilnadai-dataset-{today}.csv"'
        response.write("\ufeff")  # UTF-8 BOM for Excel Tamil text support

        writer = csv.writer(response)
        writer.writerow([
            "rule_id", "rule_category", "rule_category_english", "rule_title",
            "rule_description", "sentence_id", "sentence", "sentence_type",
            "sentence_source", "sentence_status", "created_by", "created_at",
        ])

        for rule in rules:
            for s in rule.sentences.all():
                writer.writerow([
                    rule.rule_id,
                    rule.category,
                    CATEGORY_SHORT.get(rule.category, rule.category),
                    rule.title,
                    rule.description,
                    s.sentence_id,
                    s.sentence,
                    s.sentence_type,
                    s.source,
                    s.status,
                    s.created_by.username if s.created_by else "",
                    s.created_at.isoformat() if s.created_at else "",
                ])

        return response

    # JSON — hierarchical
    data = {
        "metadata": {
            "project": "Tamil Nadai Workbench",
            "description": "Tamil writing convention rules and example sentences",
            "source": "Tamil Virtual University Style Guide (tamilvu.org)",
            "licence": "GNU GPL v3",
            "url": "https://tamilnadai-90344691621.asia-southeast1.run.app",
            "exported_at": timezone.now().isoformat(),
            "total_rules": rules.count(),
            "total_sentences": Sentence.objects.count(),
        },
        "rules": [],
    }

    for rule in rules:
        rule_data = {
            "rule_id": rule.rule_id,
            "category": rule.category,
            "category_english": CATEGORY_SHORT.get(rule.category, rule.category),
            "title": rule.title,
            "description": rule.description,
            "example_1": rule.example_1,
            "example_2": rule.example_2,
            "source": rule.source.name if rule.source else "",
            "source_page": rule.source_page,
            "sentences": [],
        }
        for s in rule.sentences.all():
            rule_data["sentences"].append({
                "sentence_id": s.sentence_id,
                "sentence": s.sentence,
                "type": s.sentence_type,
                "source": s.source,
                "status": s.status,
                "created_by": s.created_by.username if s.created_by else "",
                "created_at": s.created_at.isoformat() if s.created_at else "",
            })
        data["rules"].append(rule_data)

    content = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(content, content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="tamilnadai-dataset-{today}.json"'
    return response


@login_required
def export_eval_run(request, run_id, fmt):
    """Download results from a single evaluation run as CSV or JSON."""
    if fmt not in ("csv", "json"):
        return HttpResponse("Invalid format. Use .csv or .json", status=400)

    eval_run = get_object_or_404(EvalRun, id=run_id)
    results = (
        eval_run.results
        .select_related("sentence", "sentence__rule")
        .order_by("sentence__sentence_id")
    )
    today = timezone.now().strftime("%Y-%m-%d")
    model_slug = eval_run.model_name

    if fmt == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="tamilnadai-eval-{model_slug}-{today}.csv"'
        )
        response.write("\ufeff")  # UTF-8 BOM

        # Metadata as comments
        response.write(f"# Tamil Nadai Evaluation Results\n")
        response.write(f"# Model: {eval_run.get_model_name_display()}\n")
        response.write(f"# Date: {eval_run.created_at.strftime('%d %b %Y %H:%M')}\n")
        response.write(f"# Sentences: {eval_run.total_sentences}\n")
        if eval_run.detection_rate is not None:
            response.write(f"# Detection Rate: {eval_run.detection_rate}%\n")
        if eval_run.correction_accuracy is not None:
            response.write(f"# Correction Accuracy: {eval_run.correction_accuracy}%\n")
        if eval_run.false_positive_rate is not None:
            response.write(f"# False Positive Rate: {eval_run.false_positive_rate}%\n")
        if eval_run.category_filter:
            response.write(f"# Category: {eval_run.category_filter}\n")
        response.write(f"# Status Filter: {eval_run.get_status_filter_display()}\n")

        writer = csv.writer(response)
        writer.writerow([
            "sentence_id", "rule_id", "rule_category", "sentence_type",
            "original_sentence", "model_response", "outcome",
        ])

        for r in results:
            writer.writerow([
                r.sentence.sentence_id,
                r.sentence.rule.rule_id,
                r.sentence.rule.category,
                r.sentence.sentence_type,
                r.sentence.sentence,
                r.model_response,
                r.outcome,
            ])

        return response

    # JSON
    data = {
        "metadata": {
            "project": "Tamil Nadai Workbench",
            "model": eval_run.get_model_name_display(),
            "model_id": eval_run.model_name,
            "run_id": eval_run.id,
            "run_by": eval_run.run_by.username,
            "created_at": eval_run.created_at.isoformat(),
            "category_filter": eval_run.category_filter or None,
            "status_filter": eval_run.status_filter,
            "total_sentences": eval_run.total_sentences,
            "detection_rate": eval_run.detection_rate,
            "correction_accuracy": eval_run.correction_accuracy,
            "false_positive_rate": eval_run.false_positive_rate,
        },
        "results": [],
    }

    for r in results:
        data["results"].append({
            "sentence_id": r.sentence.sentence_id,
            "rule_id": r.sentence.rule.rule_id,
            "rule_category": r.sentence.rule.category,
            "sentence_type": r.sentence.sentence_type,
            "original_sentence": r.sentence.sentence,
            "model_response": r.model_response,
            "outcome": r.outcome,
        })

    content = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(content, content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="tamilnadai-eval-{model_slug}-{today}.json"'
    )
    return response
