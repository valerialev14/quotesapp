from django.contrib import admin
from .models import Source, Quote
from .forms import QuoteForm

class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm

admin.site.register(Source)
admin.site.register(Quote, QuoteAdmin)