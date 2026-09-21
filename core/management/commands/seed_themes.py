from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Theme

SEED_DIR = Path(__file__).resolve().parents[2] / 'seed_data' / 'themes'
DEMO_URL = 'https://templates.osonsayt.uz/?theme={slug}'

THEMES = [
    {
        'slug': 'auto-service',
        'name': 'Автосервис',
        'description': 'Услуги, цены, мастера и онлайн-запись на ремонт',
    },
    {
        'slug': 'legal',
        'name': 'Юридические услуги',
        'description': 'Практики, команда юристов, тарифы и консультации',
    },
    {
        'slug': 'beauty',
        'name': 'Салон красоты',
        'description': 'Услуги, мастера, портфолио и онлайн-запись',
    },
    {
        'slug': 'bozor',
        'name': 'Интернет-магазин',
        'description': 'Каталог товаров, акции, доставка и заявки',
    },
    {
        'slug': 'real-estate',
        'name': 'Недвижимость',
        'description': 'Объекты, галерея, агенты и заявки на просмотр',
    },
    {
        'slug': 'construction',
        'name': 'Строительство и Ремонт',
        'description': 'Услуги, портфолио, отзывы и контакты',
    },
    {
        'slug': 'education',
        'name': 'Образование',
        'description': 'Курсы, преподаватели, тарифы и отзывы',
    },
    {
        'slug': 'retail',
        'name': 'Розница',
        'description': 'Товары, услуги, акции и контакты',
    },
]

class Command(BaseCommand):
    help = 'Replaces all themes with the templates from core/seed_data/themes'

    @transaction.atomic
    def handle(self, *args, **options):
        for theme in Theme.objects.all():
            theme.image.delete(save=False)
        theme_count, _ = Theme.objects.all().delete()
        self.stdout.write(self.style.WARNING(
            f'Deleted {theme_count} existing theme records.'
        ))

        for data in THEMES:
            theme = Theme(
                name=data['name'],
                description=data['description'],
                demo_url=DEMO_URL.format(slug=data['slug']),
            )
            image_path = SEED_DIR / f"{data['slug']}.jpg"
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    theme.image.save(f"{data['slug']}.jpg", File(f), save=False)
            theme.save()
            self.stdout.write(f"  + {theme.name}")

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(THEMES)} themes.'))
