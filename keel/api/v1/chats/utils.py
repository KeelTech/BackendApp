from django.contrib.auth import get_user_model
from keel.authentication.models import CustomerProfile, AgentProfile

User = get_user_model()


def extract_user_details(user):

    if user.user_type == User.CUSTOMER:
        customer = CustomerProfile.objects.get(user=user)
        full_name = "{} {}".format(customer.first_name, customer.last_name)
        return full_name
    
    if user.user_type == User.RCIC:
        agent = AgentProfile.objects.get(agent=user)
        return agent.full_name

