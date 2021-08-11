import json
from django.core.management.base import BaseCommand
from keel.Core.models import Country, City


class Command(BaseCommand):
    help = "Create instance of cities. THIS COMMAND SHOULD ONLY BE USED ONCE"

    def handle(self, *args, **kwargs):
        f = open("countries+cities.json")
        data = json.load(f)
        
        for i in data:
            # get instance of country in Country model
            name = i.get("name")
            country = Country.objects.filter(name=name).first()
            
            for city in i["cities"]:
                # print("Country: {}, City {}".format(name, city["name"]))
                City.objects.create(country=country, city_name=city["name"])
                self.stdout.write("City {} created successfully".format(city)) 
