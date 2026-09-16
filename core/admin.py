from django.contrib import admin
from .models import Theme, Testimonial, FAQ, SiteSettings, TranslationMessage

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'demo_url')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author', 'role')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    pass

from django.core.cache import cache

@admin.register(TranslationMessage)
class TranslationMessageAdmin(admin.ModelAdmin):
    list_display = ('key', 'ru_value', 'uz_value')
    search_fields = ('key', 'ru_value', 'uz_value')
    actions = ['clear_cache']

    @admin.action(description='Clear cache for translations')
    def clear_cache(self, request, queryset):
        cache.clear()
        self.message_user(request, "Cache cleared successfully.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(f"msg_ru_{obj.key}")
        cache.delete(f"msg_uz_{obj.key}")

