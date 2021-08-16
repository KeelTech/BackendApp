import json
from django.core.management.base import BaseCommand
from keel.Core.models import State, City


class Command(BaseCommand):
    help = "Create instance of cities. THIS COMMAND SHOULD ONLY BE USED ONCE"

    def handle(self, *args, **kwargs):
        f = open("states+cities.json")
        data = json.load(f)
        
        for i in data:
            # get instance of country in Country model
            name = i.get("name")
            state = State.objects.filter(state=name).first()
            
            for city in i["cities"]:
                # print("Country: {}, City {}".format(name, city["name"]))
                city_name = city.get("name")
                City.objects.create(state=state, city_name=city_name)
                self.stdout.write("City {} created successfully".format(city)) 
