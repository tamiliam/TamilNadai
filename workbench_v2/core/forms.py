"""Forms for TamilNadai Workbench v2."""

from django import forms
from django.contrib.auth.models import User

from .models import Rule, Sentence, Source, MemberProfile


class RuleForm(forms.ModelForm):
    """Form for creating/editing a rule (admin only)."""

    class Meta:
        model = Rule
        fields = [
            "rule_id", "category", "title", "subtitle", "description",
            "example_1", "example_2", "source", "source_page",
        ]
        widgets = {
            "rule_id": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2", "placeholder": "e.g. 2.4அ"}),
            "category": forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            "title": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "subtitle": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "description": forms.Textarea(attrs={"class": "w-full border rounded px-3 py-2", "rows": 3}),
            "example_1": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "example_2": forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2"}),
            "source": forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            "source_page": forms.NumberInput(attrs={"class": "w-full border rounded px-3 py-2"}),
        }

    CATEGORY_CHOICES = [
        ("இலக்கண அமைப்பில் சொற்கள்", "இலக்கண அமைப்பில் சொற்கள் (Grammar Structure)"),
        ("தனிச் சொற்களை எழுதும் முறை", "தனிச் சொற்களை எழுதும் முறை (Individual Words)"),
        ("சந்தி", "சந்தி (Sandhi)"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget = forms.Select(
            choices=[("", "Select category...")] + self.CATEGORY_CHOICES,
            attrs={"class": "w-full border rounded px-3 py-2"},
        )


class SentenceForm(forms.Form):
    """Form for adding a sentence manually (admin only)."""

    sentence = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full border rounded px-3 py-2",
            "placeholder": "Enter Tamil sentence...",
        })
    )
    sentence_type = forms.ChoiceField(
        choices=[("correct", "Correct"), ("wrong", "Wrong")],
        widget=forms.Select(attrs={"class": "border rounded px-3 py-2"}),
    )


class ReviewForm(forms.Form):
    """Form for reviewing a sentence (accept/reject + comment)."""

    action = forms.ChoiceField(choices=[("accept", "Accept"), ("reject", "Reject")])
    comment = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "w-full border rounded px-2 py-1 text-sm", "placeholder": "Optional comment..."}
    ))


class DiscussionForm(forms.Form):
    """Form for posting a discussion message."""

    message = forms.CharField(widget=forms.Textarea(attrs={
        "class": "w-full border rounded px-3 py-2",
        "rows": 2,
        "placeholder": "Discuss this rule... (reference sentences by ID, e.g. SEN-00042)",
    }))


class ProfileForm(forms.Form):
    """Form for updating user profile."""

    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch"}
    ))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch"}
    ))
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch"}
    ))
    affiliation = forms.CharField(max_length=200, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "e.g. University of Malaya"}
    ))


class InvitationForm(forms.Form):
    """Invitation form for non-admin users (role fixed to member)."""

    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Optional: invitee's email"}
    ))


class AdminInvitationForm(forms.Form):
    """Invitation form for admin users (can set role)."""

    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Optional: invitee's email"}
    ))
    role = forms.ChoiceField(
        choices=MemberProfile.ROLE_CHOICES,
        initial="member",
        widget=forms.Select(
            attrs={"class": "border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch"}
        ),
    )


class RegistrationForm(forms.Form):
    """Registration form for invited users."""

    username = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Choose a username"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Choose a password"}
    ))
    password_confirm = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Confirm password"}
    ))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "First name"}
    ))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "Last name"}
    ))
    affiliation = forms.CharField(max_length=200, required=False, widget=forms.TextInput(
        attrs={"class": "w-full border border-grain rounded-lg px-4 py-2 text-sm bg-leaf-50 text-etch",
               "placeholder": "e.g. University of Malaya"}
    ))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        pw2 = cleaned.get("password_confirm")
        if pw and pw2 and pw != pw2:
            self.add_error("password_confirm", "Passwords do not match.")
        return cleaned
