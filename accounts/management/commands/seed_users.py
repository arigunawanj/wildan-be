from django.core.management.base import BaseCommand
from accounts.models import User

SEED_USERS = [
    ('admin', 'admin123', User.Role.ADMIN),
    ('sales1', 'sales123', User.Role.SALES),
    ('gudang1', 'gudang123', User.Role.GUDANG),
]


class Command(BaseCommand):
    help = 'Create default admin/sales/gudang users for local development'

    def handle(self, *args, **options):
        for username, password, role in SEED_USERS:
            user, created = User.objects.get_or_create(
                username=username, defaults={'role': role}
            )
            if created:
                user.set_password(password)
                if role == User.Role.ADMIN:
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created {username} ({role})'))
            else:
                self.stdout.write(f'{username} already exists, skipping')
