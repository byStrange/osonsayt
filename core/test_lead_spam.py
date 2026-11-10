import time, re
from unittest import mock
from django.test import TestCase, override_settings
from django.core.cache import cache
from core.views import lead_form_token, LEAD_TS_SALT
from core.models import SiteSettings
from django.core import signing

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class LeadTests(TestCase):
    def setUp(self):
        cache.clear()
        SiteSettings.objects.create(telegram_chat_id='-100')
        self.old_ts = signing.dumps(time.time() - 10, salt=LEAD_TS_SALT)
    def post(self, **kw):
        data = {'name': 'Ali Valiyev', 'phone': '+998 (90) 123-45-67', 'message': 'hi', 'ts': self.old_ts}
        data.update(kw)
        with mock.patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'x'}), mock.patch('urllib.request.urlopen') as m:
            r = self.client.post('/submit-lead/', data, REMOTE_ADDR=kw.pop('ip', '1.1.1.1'))
        return r, m
    def test_ok(self):
        r, m = self.post(name='<b>x</b> Ali')
        self.assertEqual(r.status_code, 302); self.assertEqual(m.call_count, 1)
        self.assertIn('&lt;b&gt;', m.call_args[0][0].data.decode())
    def test_honeypot(self): self.assertEqual(self.post(website='x')[1].call_count, 0)
    def test_no_ts(self): self.assertEqual(self.post(ts='')[1].call_count, 0)
    def test_too_fast(self): self.assertEqual(self.post(ts=lead_form_token())[1].call_count, 0)
    def test_bad_phone(self): self.assertEqual(self.post(phone='123')[1].call_count, 0)
    def test_link(self): self.assertEqual(self.post(message='visit http://spam')[1].call_count, 0)
    def test_dup_phone(self):
        self.assertEqual(self.post()[1].call_count, 1); self.assertEqual(self.post()[1].call_count, 0)
    def test_ip_limit(self):
        sent = sum(self.post(phone=f'90123456{i}')[1].call_count for i in range(6))
        self.assertEqual(sent, 3)
    def test_home_renders_form(self):
        html = self.client.get('/').content.decode()
        self.assertIn('name="ts"', html); self.assertIn('name="website"', html)


class MediaServingTests(TestCase):
    def test_media_served_with_debug_off(self):
        import tempfile, os
        from django.conf import settings
        self.assertFalse(settings.DEBUG)
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, 'x.txt'), 'w').write('ok')
            with override_settings(MEDIA_ROOT=d):
                from django.urls import clear_url_caches
                import importlib, osonsayt_project.urls as u
                importlib.reload(u); clear_url_caches()
                try:
                    r = self.client.get('/media/x.txt')
                    self.assertEqual(r.status_code, 200)
                    self.assertIn(self.client.get('/media/../manage.py').status_code, (400, 404))
                finally:
                    importlib.reload(u); clear_url_caches()
