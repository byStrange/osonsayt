from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import FAQ, SiteSettings, Testimonial, Theme, TranslationMessage


class ActiveToggleMixin:
    """Adds an inline on/off switch in the changelist plus bulk activate actions."""

    actions = ['activate_selected', 'deactivate_selected']
    list_filter = ('is_active',)
    list_editable = ('is_active',)

    @admin.action(description="Show selected on the site")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} item(s) are now visible on the site.")

    @admin.action(description="Hide selected from the site")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} item(s) are now hidden from the site.")


# Re-register the auth models so they are styled by Unfold as well.
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Theme)
class ThemeAdmin(ActiveToggleMixin, ModelAdmin):
    list_display = ('preview', 'name', 'description', 'demo_url', 'is_active')
    list_display_links = ('preview', 'name')
    search_fields = ('name', 'description')
    ordering = ('order', 'id')
    # Renders drag & drop handles in the changelist so the order of the themes
    # on the landing page can be changed by the admin.
    ordering_field = 'order'
    hide_ordering_field = True

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="height:44px;width:70px;object-fit:cover;'
            'object-position:top;border-radius:6px;" />',
            obj.image.url,
        )


@admin.register(Testimonial)
class TestimonialAdmin(ActiveToggleMixin, ModelAdmin):
    list_display = ('author', 'role', 'is_active')
    list_display_links = ('author',)
    search_fields = ('author', 'author_uz', 'role', 'quote')
    fieldsets = (
        (None, {'fields': ('photo', 'is_active')}),
        ("Русский", {'fields': ('author', 'role', 'quote')}),
        ("O'zbekcha", {'fields': ('author_uz', 'role_uz', 'quote_uz')}),
    )


@admin.register(FAQ)
class FAQAdmin(ActiveToggleMixin, ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_display_links = ('question',)
    search_fields = ('question', 'question_uz', 'answer')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    fieldsets = (
        (None, {'fields': ('is_active',)}),
        ("Русский", {'fields': ('question', 'answer')}),
        ("O'zbekcha", {'fields': ('question_uz', 'answer_uz')}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ('__str__', 'phone', 'email')
    fieldsets = (
        ("Contacts", {'fields': ('phone', 'email', 'address')}),
        ("Social", {'fields': ('telegram', 'instagram')}),
        ("Telegram leads", {'fields': ('telegram_chat_id',)}),
    )

    def has_add_permission(self, request):
        # Singleton: only one settings row makes sense.
        return not SiteSettings.objects.exists()


@admin.register(TranslationMessage)
class TranslationMessageAdmin(ModelAdmin):
    list_display = ('key', 'ru_value', 'uz_value')
    list_editable = ('ru_value', 'uz_value')
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
