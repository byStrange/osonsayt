from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import TranslationMessage

class Command(BaseCommand):
    help = 'Truncates the TranslationMessage table and cleanly loads the translations_fixture.json'

    def handle(self, *args, **options):
        # Delete all existing translations to ensure a clean slate
        count, _ = TranslationMessage.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'Deleted {count} existing translation records.'))
        
        # Load the fixture
        self.stdout.write(self.style.SUCCESS('Loading fresh translations from fixture...'))
        call_command('loaddata', 'translations_fixture.json')
        
        self.stdout.write(self.style.SUCCESS('Successfully truncated and loaded all translations!'))
