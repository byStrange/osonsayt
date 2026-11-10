from django.shortcuts import get_object_or_404, render
from .models import Theme, Testimonial, FAQ, LegalPage, SiteSettings

def _shared_context():
    """Data used by the header and footer, which are rendered on every public page."""
    return {
        'site_settings': SiteSettings.objects.first(),
        'themes': Theme.objects.filter(is_active=True),
        'faqs': FAQ.objects.filter(is_active=True),
        'legal_pages': LegalPage.objects.filter(is_active=True),
        'lead_ts': lead_form_token(),
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

import html
import json
import logging
import os
import re
import time
import urllib.request

from core.utils import get_translation
from django.contrib import messages
from django.core import signing
from django.core.cache import cache
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

# Anti-spam settings for the lead form.
LEAD_MIN_FILL_SECONDS = 3          # humans need longer than this to fill the form
LEAD_FORM_MAX_AGE = 6 * 60 * 60    # signed form timestamp is valid for 6 hours
LEAD_IP_LIMIT = 3                  # leads per IP ...
LEAD_IP_WINDOW = 10 * 60           # ... per 10 minutes
LEAD_PHONE_WINDOW = 24 * 60 * 60   # the same phone number is forwarded once a day
LEAD_TS_SALT = 'core.lead_form_ts'
URL_RE = re.compile(r'https?://|www\.|t\.me/|<a\s', re.IGNORECASE)


def lead_form_token():
    """Signed render time of the lead form, checked by submit_lead."""
    return signing.dumps(time.time(), salt=LEAD_TS_SALT)


def _client_ip(request):
    # The public proxy appends the real client address as the last
    # X-Forwarded-For entry; earlier entries can be forged by the client.
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[-1].strip()
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')


def _incr(key, timeout):
    if cache.add(key, 1, timeout):
        return 1
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout)
        return 1


def _success(request):
    messages.success(request, get_translation(request, "form_success", "Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время."))
    return redirect('/#contact')


def _drop(request, ip, reason):
    """Silently discard a spam submission; the bot sees the normal success page."""
    logger.warning("lead dropped (%s) ip=%s", reason, ip)
    return _success(request)


@require_POST
def submit_lead(request):
    ip = _client_ip(request)

    # 1. Honeypot: a hidden field real visitors never see or fill.
    if request.POST.get('website'):
        return _drop(request, ip, 'honeypot')

    # 2. The form must have been rendered by us, and not filled instantly.
    try:
        rendered_at = signing.loads(request.POST.get('ts', ''), salt=LEAD_TS_SALT, max_age=LEAD_FORM_MAX_AGE)
    except signing.BadSignature:
        return _drop(request, ip, 'bad or expired ts')
    if time.time() - float(rendered_at) < LEAD_MIN_FILL_SECONDS:
        return _drop(request, ip, 'too fast')

    # 3. Rate limit per IP.
    if _incr(f'lead:ip:{ip}', LEAD_IP_WINDOW) > LEAD_IP_LIMIT:
        return _drop(request, ip, 'ip rate limit')

    # 4. Validate the fields.
    name = ' '.join(request.POST.get('name', '').split())[:80]
    message_text = request.POST.get('message', '').strip()[:1000]
    phone = re.sub(r'\D', '', request.POST.get('phone', ''))
    if phone.startswith('998') and len(phone) == 12:
        phone = phone[3:]
    if len(name) < 2 or len(phone) != 9:
        messages.error(request, get_translation(request, "form_invalid", "Пожалуйста, укажите имя и корректный номер телефона."))
        return redirect('/#contact')
    if URL_RE.search(name) or URL_RE.search(message_text):
        return _drop(request, ip, 'link in text')

    # 5. Forward each phone number at most once per day.
    if not cache.add(f'lead:phone:{phone}', 1, LEAD_PHONE_WINDOW):
        return _drop(request, ip, f'duplicate phone {phone}')

    settings = SiteSettings.objects.first()
    chat_id = settings.telegram_chat_id if settings else None
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not (chat_id and bot_token):
        messages.error(request, get_translation(request, "form_disabled", "Сервис временно недоступен (не настроен Telegram)."))
        return redirect('/#contact')

    text = "🚨 <b>Новая заявка (OsonSayt)</b>\n\n"
    text += f"👤 <b>Имя:</b> {html.escape(name)}\n"
    text += f"📞 <b>Телефон:</b> +998{phone}\n"
    if message_text:
        text += f"💬 <b>Сообщение:</b> {html.escape(message_text)}\n"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        logger.exception("failed to forward lead to Telegram")
        cache.delete(f'lead:phone:{phone}')  # let the visitor retry
        messages.error(request, get_translation(request, "form_error", "Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже или свяжитесь с нами по телефону."))
        return redirect('/#contact')
    return _success(request)
