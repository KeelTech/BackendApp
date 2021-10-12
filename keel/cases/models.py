import uuid
from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.plans.models import Plan
from keel.authentication.models import User

from .constants import SORT_COLUMN_MAP


class CaseManager(models.Manager):

    def get_agent_cases(self, agent, req_dict):

        sort_column = req_dict.get("sort_column")
        sort_order = req_dict.get("sort_order")

        sort_list = ["-updated_at"] # default sort
        if sort_column:
            colmn_value = SORT_COLUMN_MAP.get(sort_column, "")
            if colmn_value and sort_order:
                sort_order_value = "" if sort_order == "asc" else "-"
                sort_list = [sort_order_value + colmn_value]

        queryset = self.filter(agent = agent).order_by(*sort_list)

        return queryset

    def create_from_payment(self, customer_id, plan_id):
        agent = User.objects.filter(is_active=True, user_type=User.RCIC).first()
        user = User.objects.get(pk=customer_id)
        plan = Plan.objects.get(pk=plan_id)
        return self.create(user=user, plan=plan, agent=agent)

    def update_plan_agent(self, case_id, plan_id):
        case_modle_obj = self.select_for_update().get(pk=case_id)
        case_modle_obj.agent = User.objects.filter(is_active=True, user_type=User.RCIC).first()
        if case_modle_obj.plan.pk != plan_id:
            case_modle_obj.plan = Plan.objects.get(pk=plan_id)
        case_modle_obj.save()
        return case_modle_obj


class Case(TimeStampedModel, SoftDeleteModel):

    BOOKED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELLED = 4

    CASES_TYPE_CHOICES = (
        (BOOKED, 'BOOKED'),
        (IN_PROGRESS, 'IN_PROGRESS'),
        (COMPLETED, 'COMPLETED'),
        (CANCELLED, 'CANCELLED'),
    )

    case_id = models.CharField(max_length=255, primary_key=True)
    display_id = models.CharField(max_length=5, default=None, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases',
                              null=True, blank=True)
    account_manager = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='account_manager_cases',
                                        null=True, blank=True, default=None)
    status = models.PositiveSmallIntegerField(choices=CASES_TYPE_CHOICES, verbose_name="case_status", default=BOOKED)
    is_active = models.BooleanField(verbose_name= 'Active', default=True)
    ref_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.deletion.DO_NOTHING)
    plan = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING, related_name='plans_cases')
    # new program field
    program = models.CharField(max_length=512, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.case_id:
            self.case_id = uuid.uuid4()
        if not self.display_id:
            reverse_case_id=str(self.case_id)[::-1]
            self.display_id=(reverse_case_id[0:5])[::-1]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.case_id)

    objects = CaseManager()


class Program(TimeStampedModel, SoftDeleteModel):
    
    EXPRESS_ENTRY = "Express Entry"
    PROVINCIAL_NOMINATION  = "Provincial Nomination"
    INVESTORS = "Investors"
    FAMILY_SPONSORSHIP = "Family Sponsorship"

    CHOICES_CATEGORY = (
        (EXPRESS_ENTRY, 'EXPRESS_ENTRY'),
        (PROVINCIAL_NOMINATION, 'PROVINCIAL_NOMINATION'),
        (INVESTORS, 'INVESTORS'),
        (FAMILY_SPONSORSHIP, 'FAMILY_SPONSORSHIP')
    )

    choice = models.CharField(max_length=512, default=None, blank=True, null=True)
    category = models.CharField(max_length=512, choices=CHOICES_CATEGORY, default=EXPRESS_ENTRY)
    
    def __str__(self) -> str:
        return self.choice