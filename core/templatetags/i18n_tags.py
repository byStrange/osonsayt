from django import template
from django.core.cache import cache
from core.models import TranslationMessage
import logging
from core.utils import get_translation
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def t(context, key, default_text):
    request = context.get('request')
    return mark_safe(get_translation(request, key, default_text))

