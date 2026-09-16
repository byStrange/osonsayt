from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Theme, ThemeCategory

SEED_DIR = Path(__file__).resolve().parents[2] / 'seed_data' / 'themes'
DEMO_URL = 'https://e-shop.triger.uz/?theme={slug}'

# slug matches the theme directory in the vizitka project and the screenshot file name
THEMES = [
    {
        'slug': 'auto-service',
        'name': 'Автосервис',
        'category': 'Авто',
        'description': 'Услуги, цены, мастера и онлайн-запись на ремонт',
    },
    {
        'slug': 'legal',
        'name': 'Юридические услуги',
        'category': 'Юристы',
        'description': 'Практики, команда юристов, тарифы и консультации',
    },
    {
        'slug': 'medicine',
        'name': 'Клиника',
        'category': 'Медицина',
        'description': 'Услуги, врачи, цены и запись на приём',
    },
    {
        'slug': 'beauty',
        'name': 'Салон красоты',
        'category': 'Красота',
        'description': 'Услуги, мастера, портфолио и онлайн-запись',
    },
    {
        'slug': 'bozor',
        'name': 'Интернет-магазин',
        'category': 'Магазин',
        'description': 'Каталог товаров, акции, доставка и заявки',
    },
    {
        'slug': 'real-estate',
        'name': 'Недвижимость',
        'category': 'Недвижимость',
        'description': 'Объекты, галерея, агенты и заявки на просмотр',
    },
]


class Command(BaseCommand):
    help = 'Replaces all themes and theme categories with the templates from core/seed_data/themes'

    @transaction.atomic
    def handle(self, *args, **options):
        for theme in Theme.objects.all():
            theme.image.delete(save=False)
        theme_count, _ = Theme.objects.all().delete()
        category_count, _ = ThemeCategory.objects.all().delete()
        self.stdout.write(self.style.WARNING(
            f'Deleted {theme_count} existing theme and {category_count} category records.'
        ))

        for data in THEMES:
            category, _ = ThemeCategory.objects.get_or_create(
                slug=data['slug'], defaults={'name': data['category']}
            )
            theme = Theme(
                name=data['name'],
                description=data['description'],
                category=category,
                demo_url=DEMO_URL.format(slug=data['slug']),
            )
            with open(SEED_DIR / f"{data['slug']}.jpg", 'rb') as f:
                theme.image.save(f"{data['slug']}.jpg", File(f), save=False)
            theme.save()
            self.stdout.write(f"  + {theme.name}")

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(THEMES)} themes.'))
