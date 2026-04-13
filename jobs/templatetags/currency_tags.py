from django import template

register = template.Library()

SYMBOLS = {
    'EUR': '€',
    'USD': '$',
    'GBP': '£',
    'CAD': 'CA$',
    'AUD': 'AU$',
}

@register.filter
def currency_symbol(currency_code):
    return SYMBOLS.get(currency_code, currency_code)