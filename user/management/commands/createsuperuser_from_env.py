from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Creates an admin user non-interactively given the data from environment variables."

    def handle(self, *args, **options):
        User = get_user_model()
        DEFAULT_ADMIN = settings.DEFAULT_ADMIN
        try:
            user, created = User.objects.get_or_create(
                username=DEFAULT_ADMIN["username"],
                email=DEFAULT_ADMIN["email"],
                is_staff=True,
                is_superuser=True,
            )
            if not created:
                self.stdout.write(
                    self.style.WARNING(
                        "A superuser with provided credentials already exists."
                    )
                )
            else:
                user.set_password(DEFAULT_ADMIN["password"])
                self.stdout.write(self.style.SUCCESS("Created a superuser."))
        except IntegrityError as ie:
            self.stderr.write(
                self.style.ERROR(
                    f"Cannot create a new user with such credentials. {ie}"
                )
            )
