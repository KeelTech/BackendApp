import json
from django.core.management.base import BaseCommand
from keel.Core.models import Country, State


class Command(BaseCommand):
    help = "Create instance of cities. THIS COMMAND SHOULD ONLY BE USED ONCE"

    def handle(self, *args, **kwargs):
        f = open("countries+states.json")
        data = json.load(f)
        
        for i in data:
            # get instance of country in Country model
            name = i.get("name")
            country = Country.objects.filter(name=name).first()

            for state in i["states"]:
                # print("Country: {}, City {}".format(name, city["name"]))
                state = state.get('name')
                State.objects.create(country=country, state=state)
                self.stdout.write("State {} created successfully".format(state))