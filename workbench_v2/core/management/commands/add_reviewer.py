"""Management command to add a reviewer user."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import MemberProfile


class Command(BaseCommand):
    help = "Create a user for the workbench with a specified role"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("--name", type=str, default="", help="Full name")
        parser.add_argument("--admin", action="store_true", help="Make this user an admin (staff)")
        parser.add_argument(
            "--role", type=str, default="", choices=["admin", "reviewer", "member"],
            help="Role: admin, reviewer, or member (default: reviewer, or admin if --admin)"
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        name = options["name"]
        is_admin = options["admin"]

        # Determine role
        if options["role"]:
            role = options["role"]
        elif is_admin:
            role = "admin"
        else:
            role = "reviewer"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            return

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=(role == "admin"),
        )

        if name:
            parts = name.split(" ", 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save()

        MemberProfile.objects.create(user=user, role=role)

        self.stdout.write(self.style.SUCCESS(
            f"Created {role}: {username}" + (f" ({name})" if name else "")
        ))
