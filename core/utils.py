from django.core.cache import cache
from core.models import TranslationMessage

def get_translation(request, key, default_text):
    lang = getattr(request, 'LANGUAGE_CODE', 'ru') if request else 'ru'
    cache_key = f"msg_{lang}_{key}"
    
    cached_value = cache.get(cache_key)
    if cached_value:
        return cached_value

    msg, created = TranslationMessage.objects.get_or_create(
        key=key,
        defaults={'ru_value': default_text}
    )
    
    if lang == 'uz' and msg.uz_value:
        value_to_return = msg.uz_value
    else:
        value_to_return = msg.ru_value if msg.ru_value else default_text
        
    cache.set(cache_key, value_to_return, timeout=60*60*24*30) # 30 days
    return value_to_return
