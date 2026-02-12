"""Tests for TamilNadai Workbench v2."""

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from .models import MemberProfile, Rule, Source, Sentence, EvalRun, EvalResult


class PublicPageTests(TestCase):
    """Static pages should be accessible without login."""

    def test_about_page(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tamil Nadai")

    def test_privacy_page(self):
        response = self.client.get(reverse("privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Privacy Policy")

    def test_terms_page(self):
        response = self.client.get(reverse("terms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Terms of Service")

    def test_cookies_page(self):
        response = self.client.get(reverse("cookies"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cookie Policy")

    def test_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_about_footer_links(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, 'href="/privacy/"')
        self.assertContains(response, 'href="/terms/"')
        self.assertContains(response, 'href="/cookies/"')
        self.assertContains(response, "tamiliam@gmail.com")
        self.assertContains(response, "2026 Tamil Nadai")

    def test_about_shows_sign_in_for_anonymous(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "Sign in")
        self.assertNotContains(response, "Sign out")

    def test_about_shows_gnu_gpl(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, "GNU General Public License")


class URLResolutionTests(TestCase):
    """All URL patterns should resolve to the correct view."""

    def test_public_urls_resolve(self):
        for name in ("about", "privacy", "terms", "cookies", "login"):
            url = reverse(name)
            self.assertEqual(resolve(url).url_name, name)

    def test_authenticated_urls_resolve(self):
        for name in ("dashboard", "rule_list", "review_queue", "review_log",
                      "profile", "members_list", "invite"):
            url = reverse(name)
            self.assertEqual(resolve(url).url_name, name)


class AuthenticationTests(TestCase):
    """Protected pages should redirect to login for anonymous users."""

    def test_dashboard_redirects_anonymous(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_rules_redirects_anonymous(self):
        response = self.client.get(reverse("rule_list"))
        self.assertEqual(response.status_code, 302)

    def test_profile_redirects_anonymous(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_review_queue_redirects_anonymous(self):
        response = self.client.get(reverse("review_queue"))
        self.assertEqual(response.status_code, 302)


class AuthenticatedPageTests(TestCase):
    """Logged-in users should be able to access main pages."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        MemberProfile.objects.create(user=self.user, role="admin")
        self.client.login(username="testuser", password="testpass123")

    def test_dashboard(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_rule_list(self):
        response = self.client.get(reverse("rule_list"))
        self.assertEqual(response.status_code, 200)

    def test_review_queue(self):
        response = self.client.get(reverse("review_queue"))
        self.assertEqual(response.status_code, 200)

    def test_review_log(self):
        response = self.client.get(reverse("review_log"))
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_members_list(self):
        response = self.client.get(reverse("members_list"))
        self.assertEqual(response.status_code, 200)

    def test_invite_page(self):
        response = self.client.get(reverse("invite"))
        self.assertEqual(response.status_code, 200)

    def test_nav_shows_sign_out(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Sign out")

    def test_nav_shows_user_role(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Admin")


class RolePermissionTests(TestCase):
    """Permission decorator should restrict access based on role."""

    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="pass123")
        MemberProfile.objects.create(user=self.admin, role="admin")

        self.reviewer = User.objects.create_user(username="reviewer", password="pass123")
        MemberProfile.objects.create(user=self.reviewer, role="reviewer")

        self.member = User.objects.create_user(username="member", password="pass123")
        MemberProfile.objects.create(user=self.member, role="member")

    def test_admin_can_access_members_list(self):
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("members_list"))
        self.assertEqual(response.status_code, 200)

    def test_reviewer_cannot_access_members_list(self):
        self.client.login(username="reviewer", password="pass123")
        response = self.client.get(reverse("members_list"))
        self.assertEqual(response.status_code, 302)  # redirects to dashboard

    def test_member_cannot_access_members_list(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("members_list"))
        self.assertEqual(response.status_code, 302)  # redirects to dashboard


class MemberProfileTests(TestCase):
    """MemberProfile model should work correctly."""

    def test_has_role_hierarchy(self):
        user = User.objects.create_user(username="test", password="pass123")
        profile = MemberProfile.objects.create(user=user, role="reviewer")
        self.assertTrue(profile.has_role("member"))
        self.assertTrue(profile.has_role("reviewer"))
        self.assertFalse(profile.has_role("admin"))

    def test_admin_has_all_roles(self):
        user = User.objects.create_user(username="test", password="pass123")
        profile = MemberProfile.objects.create(user=user, role="admin")
        self.assertTrue(profile.has_role("member"))
        self.assertTrue(profile.has_role("reviewer"))
        self.assertTrue(profile.has_role("admin"))

    def test_member_has_only_member_role(self):
        user = User.objects.create_user(username="test", password="pass123")
        profile = MemberProfile.objects.create(user=user, role="member")
        self.assertTrue(profile.has_role("member"))
        self.assertFalse(profile.has_role("reviewer"))
        self.assertFalse(profile.has_role("admin"))


class SentenceCreatedByTests(TestCase):
    """Sentence.created_by should track who added the sentence."""

    def setUp(self):
        self.source = Source.objects.create(source_id="SRC-01", name="Test Source")
        self.rule = Rule.objects.create(
            rule_id="1.1", category="சந்தி", title="Test Rule",
            source=self.source,
        )
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        MemberProfile.objects.create(user=self.admin, role="admin")
        self.member = User.objects.create_user(
            username="member", password="pass123"
        )
        MemberProfile.objects.create(user=self.member, role="member")

    def test_admin_add_sentence_sets_created_by(self):
        self.client.login(username="admin", password="pass123")
        self.client.post(reverse("add_sentence", args=[self.rule.rule_id]), {
            "sentence": "சான்று வாக்கியம்",
            "sentence_type": "correct",
        })
        s = Sentence.objects.first()
        self.assertIsNotNone(s)
        self.assertEqual(s.created_by, self.admin)
        self.assertEqual(s.source, "manual")

    def test_member_add_sentence_sets_created_by(self):
        self.client.login(username="member", password="pass123")
        self.client.post(reverse("add_sentence", args=[self.rule.rule_id]), {
            "sentence": "சான்று வாக்கியம்",
            "sentence_type": "correct",
        })
        s = Sentence.objects.first()
        self.assertIsNotNone(s)
        self.assertEqual(s.created_by, self.member)
        self.assertEqual(s.source, "proposed")

    def test_sentence_created_by_displayed_on_rule_detail(self):
        Sentence.objects.create(
            sentence_id="SEN-00001", rule=self.rule,
            sentence="சான்று", sentence_type="correct",
            source="manual", created_by=self.admin,
        )
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("rule_detail", args=[self.rule.rule_id]))
        self.assertContains(response, "admin")


class EvalViewTests(TestCase):
    """Evaluation pages should be admin-only."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        MemberProfile.objects.create(user=self.admin, role="admin")
        self.member = User.objects.create_user(
            username="member", password="pass123"
        )
        MemberProfile.objects.create(user=self.member, role="member")

    def test_evaluate_page_accessible_by_admin(self):
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("evaluate"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evaluate LLMs")

    def test_evaluate_page_redirects_member(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("evaluate"))
        self.assertEqual(response.status_code, 302)

    def test_evaluate_page_redirects_anonymous(self):
        response = self.client.get(reverse("evaluate"))
        self.assertEqual(response.status_code, 302)

    def test_evaluate_urls_resolve(self):
        for name in ("evaluate", "run_evaluation"):
            url = reverse(name)
            self.assertEqual(resolve(url).url_name, name)

    def test_admin_nav_shows_evaluate_link(self):
        self.client.login(username="admin", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Evaluate")


class EvalScoringTests(TestCase):
    """Scoring logic should classify model responses correctly."""

    def setUp(self):
        self.source = Source.objects.create(source_id="SRC-01", name="Test Source")
        self.rule = Rule.objects.create(
            rule_id="1.1", category="சந்தி", title="Test Rule",
            source=self.source,
        )
        self.correct = Sentence.objects.create(
            sentence_id="SEN-00001", rule=self.rule,
            sentence="அப்படிக் கூறினான்.", sentence_type="correct",
        )
        self.wrong = Sentence.objects.create(
            sentence_id="SEN-00002", rule=self.rule,
            sentence="அப்படி கூறினான்.", sentence_type="wrong",
        )

    def test_true_positive(self):
        from .eval_service import score_result
        result = score_result(self.wrong, "அப்படிக் கூறினான்.")
        self.assertEqual(result, "true_positive")

    def test_false_negative(self):
        from .eval_service import score_result
        result = score_result(self.wrong, "அப்படி கூறினான்.")
        self.assertEqual(result, "false_negative")

    def test_partial(self):
        from .eval_service import score_result
        result = score_result(self.wrong, "அப்படியே கூறினான்.")
        self.assertEqual(result, "partial")

    def test_true_negative(self):
        from .eval_service import score_result
        result = score_result(self.correct, "அப்படிக் கூறினான்.")
        self.assertEqual(result, "true_negative")

    def test_false_positive(self):
        from .eval_service import score_result
        result = score_result(self.correct, "அப்படி கூறினான்.")
        self.assertEqual(result, "false_positive")

    def test_error_on_empty_response(self):
        from .eval_service import score_result
        result = score_result(self.wrong, "")
        self.assertEqual(result, "error")

    def test_error_on_none_response(self):
        from .eval_service import score_result
        result = score_result(self.wrong, None)
        self.assertEqual(result, "error")


class ExportPageTests(TestCase):
    """Export page and download endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        MemberProfile.objects.create(user=self.admin, role="admin")
        self.member = User.objects.create_user(
            username="member", password="pass123"
        )
        MemberProfile.objects.create(user=self.member, role="member")

        self.source = Source.objects.create(source_id="SRC-01", name="Test Source")
        self.rule = Rule.objects.create(
            rule_id="1.1", category="சந்தி", title="Test Rule",
            source=self.source,
        )
        self.sentence = Sentence.objects.create(
            sentence_id="SEN-00001", rule=self.rule,
            sentence="அப்படிக் கூறினான்.", sentence_type="correct",
            source="book", status="accepted", created_by=self.admin,
        )

    def test_exports_page_redirects_anonymous(self):
        response = self.client.get(reverse("exports"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dataset_csv_redirects_anonymous(self):
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "csv"}))
        self.assertEqual(response.status_code, 302)

    def test_member_can_access_exports_page(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("exports"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Exports")

    def test_member_can_download_dataset_csv(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "csv"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("tamilnadai-dataset", response["Content-Disposition"])

    def test_member_can_download_dataset_json(self):
        import json
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "json"}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response["Content-Type"])
        data = json.loads(response.content)
        self.assertIn("metadata", data)
        self.assertIn("rules", data)

    def test_invalid_format_returns_400(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "xml"}))
        self.assertEqual(response.status_code, 400)

    def test_csv_contains_header_and_tamil(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "csv"}))
        content = response.content.decode("utf-8-sig")
        self.assertIn("rule_id", content)
        self.assertIn("அப்படிக் கூறினான்.", content)

    def test_csv_row_count(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "csv"}))
        content = response.content.decode("utf-8-sig")
        lines = [l for l in content.strip().split("\n") if l and not l.startswith("#")]
        self.assertEqual(len(lines), 2)  # 1 header + 1 data row

    def test_json_metadata_and_structure(self):
        import json
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("export_dataset", kwargs={"fmt": "json"}))
        data = json.loads(response.content)
        self.assertEqual(data["metadata"]["project"], "Tamil Nadai Workbench")
        self.assertIn("exported_at", data["metadata"])
        rule = data["rules"][0]
        self.assertIn("சந்தி", rule["category"])
        self.assertEqual(len(rule["sentences"]), 1)

    def test_export_urls_resolve(self):
        for name, kwargs in [
            ("exports", {}),
            ("export_dataset", {"fmt": "csv"}),
            ("export_dataset", {"fmt": "json"}),
        ]:
            url = reverse(name, kwargs=kwargs)
            self.assertEqual(resolve(url).url_name, name)

    def test_exports_nav_link_visible_for_member(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Exports")


class EvalExportTests(TestCase):
    """Test eval run download with actual eval data."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        MemberProfile.objects.create(user=self.admin, role="admin")
        self.member = User.objects.create_user(
            username="member", password="pass123"
        )
        MemberProfile.objects.create(user=self.member, role="member")

        self.source = Source.objects.create(source_id="SRC-01", name="Test Source")
        self.rule = Rule.objects.create(
            rule_id="1.1", category="சந்தி", title="Test Rule",
            source=self.source,
        )
        self.sentence = Sentence.objects.create(
            sentence_id="SEN-00001", rule=self.rule,
            sentence="அப்படி கூறினான்.", sentence_type="wrong",
        )
        self.eval_run = EvalRun.objects.create(
            model_name="gemini-2.0-flash", run_by=self.admin,
            total_sentences=1, detection_rate=100.0,
            correction_accuracy=100.0, false_positive_rate=0.0,
        )
        EvalResult.objects.create(
            eval_run=self.eval_run, sentence=self.sentence,
            model_response="அப்படிக் கூறினான்.", outcome="true_positive",
        )

    def test_eval_export_redirects_anonymous(self):
        response = self.client.get(
            reverse("export_eval_run", kwargs={"run_id": self.eval_run.id, "fmt": "csv"})
        )
        self.assertEqual(response.status_code, 302)

    def test_eval_export_404_for_missing_run(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(
            reverse("export_eval_run", kwargs={"run_id": 999, "fmt": "csv"})
        )
        self.assertEqual(response.status_code, 404)

    def test_eval_csv_has_metadata_and_data(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(
            reverse("export_eval_run", kwargs={"run_id": self.eval_run.id, "fmt": "csv"})
        )
        content = response.content.decode("utf-8-sig")
        self.assertIn("# Model:", content)
        self.assertIn("Gemini 2.0 Flash", content)
        self.assertIn("sentence_id", content)
        self.assertIn("true_positive", content)

    def test_eval_json_has_metadata_and_results(self):
        import json
        self.client.login(username="member", password="pass123")
        response = self.client.get(
            reverse("export_eval_run", kwargs={"run_id": self.eval_run.id, "fmt": "json"})
        )
        data = json.loads(response.content)
        self.assertEqual(data["metadata"]["model_id"], "gemini-2.0-flash")
        self.assertEqual(data["metadata"]["detection_rate"], 100.0)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["outcome"], "true_positive")

    def test_member_can_download_eval_results(self):
        self.client.login(username="member", password="pass123")
        response = self.client.get(
            reverse("export_eval_run", kwargs={"run_id": self.eval_run.id, "fmt": "csv"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])

    def test_eval_export_url_resolves(self):
        url = reverse("export_eval_run", kwargs={"run_id": 1, "fmt": "csv"})
        self.assertEqual(resolve(url).url_name, "export_eval_run")
