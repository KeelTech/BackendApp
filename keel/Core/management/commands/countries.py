import json
from django.core.management.base import BaseCommand
from keel.Core.models import Country


class Command(BaseCommand):
    help = "Create instance of countries. THIS COMMAND SHOULD ONLY BE USED ONCE"

    def handle(self, *args, **kwargs):
        f = open('countries+states.json')
        data = json.load(f)
        
        for i in data:
            name = i.get("name")
            numeric_code = i.get("numeric_code")
            phone_code = i.get("phone_code")
            capital = i.get("capital")
            currency = i.get("currency")
            currency_symbol = i.get("currency_symbol")

            Country.objects.create(name=name, numeric_code=numeric_code, phone_code=phone_code, capital=capital, 
                            currency=currency, currency_symbol=currency_symbol)
            
            self.stdout.write("Country {} created successfully".format(name))