from modeltranslation.translator import register, TranslationOptions
from .models import Listing

@register(Listing)
class ListingTranslationOptions(TranslationOptions):
    fields = ('description',)
