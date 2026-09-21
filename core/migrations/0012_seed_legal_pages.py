from django.db import migrations

# slug -> (TranslationMessage key used by the old footer, default ru, default uz)
PAGES = [
    ('privacy', 'politika_konfidentsialnosti', 'Политика конфиденциальности', 'Maxfiylik siyosati'),
    ('terms', 'usloviya_ispolzovaniya', 'Условия использования', 'Foydalanish shartlari'),
]


def seed_legal_pages(apps, schema_editor):
    LegalPage = apps.get_model('core', 'LegalPage')
    TranslationMessage = apps.get_model('core', 'TranslationMessage')
    for slug, key, ru, uz in PAGES:
        # Keep whatever labels the admin already set for the old hardcoded footer links.
        old = TranslationMessage.objects.filter(key=key).first()
        LegalPage.objects.get_or_create(
            slug=slug,
            defaults={
                'label': (old and old.ru_value) or ru,
                'label_uz': (old and old.uz_value) or uz,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_legalpage'),
    ]

    operations = [
        migrations.RunPython(seed_legal_pages, migrations.RunPython.noop),
    ]
