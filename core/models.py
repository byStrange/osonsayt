from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    description_uz = models.CharField(max_length=255, blank=True, null=True, verbose_name="Description (UZ)")
    image = models.ImageField(upload_to='themes/')
    demo_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Order")
    is_active = models.BooleanField(default=True, verbose_name="Active", help_text="Show this theme on the site")

    @property
    def translated_description(self):
        from django.utils.translation import get_language
        return self.description_uz if get_language() == 'uz' and self.description_uz else self.description

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    author = models.CharField(max_length=100)
    author_uz = models.CharField(max_length=100, blank=True, null=True, verbose_name="Author (UZ)")
    role = models.CharField(max_length=100)
    role_uz = models.CharField(max_length=100, blank=True, null=True, verbose_name="Role (UZ)")
    quote = models.TextField()
    quote_uz = models.TextField(blank=True, null=True, verbose_name="Quote (UZ)")
    photo = models.ImageField(upload_to='testimonials/')
    is_active = models.BooleanField(default=True, verbose_name="Active", help_text="Show this testimonial on the site")

    @property
    def translated_author(self):
        from django.utils.translation import get_language
        return self.author_uz if get_language() == 'uz' and self.author_uz else self.author

    @property
    def translated_role(self):
        from django.utils.translation import get_language
        return self.role_uz if get_language() == 'uz' and self.role_uz else self.role

    @property
    def translated_quote(self):
        from django.utils.translation import get_language
        return self.quote_uz if get_language() == 'uz' and self.quote_uz else self.quote

    def __str__(self):
        return self.author

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    question_uz = models.CharField(max_length=255, blank=True, null=True, verbose_name="Question (UZ)")
    answer = models.TextField()
    answer_uz = models.TextField(blank=True, null=True, verbose_name="Answer (UZ)")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Active", help_text="Show this question on the site")

    @property
    def translated_question(self):
        from django.utils.translation import get_language
        return self.question_uz if get_language() == 'uz' and self.question_uz else self.question

    @property
    def translated_answer(self):
        from django.utils.translation import get_language
        return self.answer_uz if get_language() == 'uz' and self.answer_uz else self.answer

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question

class SiteSettings(models.Model):
    phone = models.CharField(max_length=50, default='+998 (00) 000-00-00')
    email = models.EmailField(default='info@osonsayt.uz')
    telegram = models.URLField(blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True, help_text="Chat ID for receiving leads")
    instagram = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, default='Tashkent, Uzbekistan')

    class Meta:
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Global Site Settings"

class TranslationMessage(models.Model):
    key = models.CharField(max_length=255, unique=True)
    ru_value = models.TextField(blank=True)
    uz_value = models.TextField(blank=True)

    def __str__(self):
        return self.key
