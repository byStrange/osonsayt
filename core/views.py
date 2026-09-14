from django.shortcuts import render
from .models import ThemeCategory, Theme, Testimonial, FAQ, SiteSettings

def home(request):
    settings = SiteSettings.objects.first()
    categories = ThemeCategory.objects.all()
    themes = Theme.objects.all()
    testimonials = Testimonial.objects.all()
    faqs = FAQ.objects.all()
    
    return render(request, 'home.html', {
        'site_settings': settings,
        'categories': categories,
        'themes': themes,
        'testimonials': testimonials,
        'faqs': faqs,
    })
