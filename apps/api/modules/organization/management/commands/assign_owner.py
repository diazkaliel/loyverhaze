from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from modules.organization.models import Organization, Membership


class Command(BaseCommand):
    help = "Assign an existing user to the initial organization as owner."

    def add_arguments(self, parser):
        parser.add_argument("username")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        user = get_user_model().objects.filter(username=username, is_active=True).first()
        if user is None:
            raise CommandError("No existe un usuario activo con ese nombre.")
        org = Organization.objects.order_by("created_at").first()
        if org is None:
            raise CommandError("No existe una organización; ejecuta migrate primero.")
        membership, created = Membership.objects.get_or_create(
            organization=org, user=user, defaults={"role": Membership.Role.OWNER}
        )
        if not created and membership.role != Membership.Role.OWNER:
            membership.role = Membership.Role.OWNER
            membership.save(update_fields=["role"])
        self.stdout.write(self.style.SUCCESS(f"Usuario {username} asignado a {org.name} como propietario."))
