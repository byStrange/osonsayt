from django.db import models

class ThemeCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Theme Categories"

    def __str__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(ThemeCategory, on_delete=models.CASCADE, related_name='themes')
    image = models.ImageField(upload_to='themes/')

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    author = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    quote = models.TextField()
    photo = models.ImageField(upload_to='testimonials/')

    def __str__(self):
        return self.author

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)

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
