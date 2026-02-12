from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("rules/", views.rule_list, name="rule_list"),
    path("rules/add/", views.rule_add, name="rule_add"),
    path("rules/<str:rule_id>/", views.rule_detail, name="rule_detail"),
    path("rules/<str:rule_id>/edit/", views.rule_edit, name="rule_edit"),
    path("rules/<str:rule_id>/deactivate/", views.rule_deactivate, name="rule_deactivate"),
    path("rules/<str:rule_id>/add-sentence/", views.add_sentence, name="add_sentence"),
    path("rules/<str:rule_id>/discuss/", views.add_discussion, name="add_discussion"),
    path("rules/<str:rule_id>/ai-suggest/", views.ai_suggest, name="ai_suggest"),
    path("sentences/<str:sentence_id>/review/", views.review_sentence, name="review_sentence"),
    path("sentences/<str:sentence_id>/edit/", views.edit_sentence, name="edit_sentence"),
    path("sentences/<str:sentence_id>/delete/", views.delete_sentence, name="delete_sentence"),
    path("review-queue/", views.review_queue, name="review_queue"),
    path("review-log/", views.review_log, name="review_log"),
    # Membership module
    path("profile/", views.profile_view, name="profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("profile/avatar/", views.upload_avatar, name="upload_avatar"),
    path("members/", views.members_list, name="members_list"),
    path("members/<int:user_id>/role/", views.change_role, name="change_role"),
    path("members/<int:user_id>/remove/", views.remove_member, name="remove_member"),
    path("invite/", views.invite_member, name="invite"),
    path("register/<uuid:token>/", views.register_view, name="register"),
    path("discussion/<int:discussion_id>/delete/", views.delete_discussion, name="delete_discussion"),
    # Evaluation
    path("evaluate/", views.evaluate_view, name="evaluate"),
    path("evaluate/run/", views.run_evaluation_view, name="run_evaluation"),
    path("evaluate/<int:run_id>/", views.eval_detail, name="eval_detail"),
    path("evaluate/<int:run_id>/download.<str:fmt>", views.export_eval_run, name="export_eval_run"),
    # Exports (any logged-in member)
    path("exports/", views.exports_page, name="exports"),
    path("exports/dataset.<str:fmt>", views.export_dataset, name="export_dataset"),
    # Static pages (public)
    path("about/", views.about_view, name="about"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("terms/", views.terms_view, name="terms"),
    path("cookies/", views.cookies_view, name="cookies"),
]
