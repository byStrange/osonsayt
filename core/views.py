from django.shortcuts import get_object_or_404, render
from .models import Theme, Testimonial, FAQ, LegalPage, SiteSettings

def _shared_context():
    """Data used by the header and footer, which are rendered on every public page."""
    return {
        'site_settings': SiteSettings.objects.first(),
        'themes': Theme.objects.filter(is_active=True),
        'faqs': FAQ.objects.filter(is_active=True),
        'legal_pages': LegalPage.objects.filter(is_active=True),
    }

def home(request):
    return render(request, 'home.html', {
        **_shared_context(),
        'testimonials': Testimonial.objects.filter(is_active=True),
    })

def legal_page(request, slug):
    page = get_object_or_404(LegalPage, slug=slug, is_active=True)
    return render(request, 'legal_page.html', {
        **_shared_context(),
        'page': page,
        # Header/footer section links point to the landing page, not this one.
        'anchor_base': '/',
    })

import os
import json
import urllib.request
from core.utils import get_translation
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

@require_POST
def submit_lead(request):
    name = request.POST.get('name', '')
    raw_phone = request.POST.get('phone', '')
    # Normalize phone: extract only digits
    import re
    clean_phone = re.sub(r'\D', '', raw_phone)
    # Remove leading 998 if present
    if clean_phone.startswith('998') and len(clean_phone) == 12:
        clean_phone = clean_phone[3:]
    
    phone = clean_phone if clean_phone else raw_phone

    message_text = request.POST.get('message', '')
    
    settings = SiteSettings.objects.first()
    chat_id = settings.telegram_chat_id if settings else None
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if chat_id and bot_token:
        text = f"🚨 <b>Новая заявка (OsonSayt)</b>\n\n"
        text += f"👤 <b>Имя:</b> {name}\n"
        text += f"📞 <b>Телефон:</b> {phone}\n"
        if message_text:
            text += f"💬 <b>Сообщение:</b> {message_text}\n"
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req)
            messages.success(request, get_translation(request, "form_success", "Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время."))
        except Exception as e:
            messages.error(request, get_translation(request, "form_error", "Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону."))
    else:
        messages.error(request, get_translation(request, "form_disabled", "Сервис временно недоступен (не настроен Telegram)."))
        
    return redirect('/#contact')
