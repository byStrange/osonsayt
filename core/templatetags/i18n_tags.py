from django import template
from django.core.cache import cache
from core.models import TranslationMessage
import logging
from core.utils import get_translation

register = template.Library()

@register.simple_tag(takes_context=True)
def t(context, key, default_text):
    request = context.get('request')
    return get_translation(request, key, default_text)

