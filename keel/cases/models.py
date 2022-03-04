import uuid

from django.db import models
from keel.authentication.models import User
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.plans.models import Plan

from .constants import SORT_COLUMN_MAP


class CaseManager(models.Manager):
    def get_agent_cases(self, agent, req_dict):

        sort_column = req_dict.get("sort_column")
        sort_order = req_dict.get("sort_order")

        sort_list = ["-updated_at"]  # default sort
        if sort_column:
            colmn_value = SORT_COLUMN_MAP.get(sort_column, "")
            if colmn_value and sort_order:
                sort_order_value = "" if sort_order == "asc" else "-"
                sort_list = [sort_order_value + colmn_value]

        user_type = agent.user_type

        if user_type == User.RCIC:
            queryset = (
                self.select_related("plan", "user__user_profile", "agent")
                .prefetch_related(
                    "cases_tasks",
                )
                .filter(agent=agent)
                .order_by(*sort_list)
            )

        elif user_type == User.ACCOUNT_MANAGER:
            queryset = (
                self.select_related("plan", "user", "account_manager")
                .prefetch_related(
                    "cases_tasks",
                )
                .filter(accout_manager=agent)
                .order_by(*sort_list)
            )

        return queryset

    def check_for_unread_chats(self, obj):
        agent = obj.agent
        case_user = obj.user

        data = {"new_message": False, "message": "", "sent_date": "", "sent_by": ""}

        try:
            last_read_chat = obj.case_chats_receipts.all()
            filter = [x for x in last_read_chat if x.user_id == agent]

            last_read_chat = 0

            if len(filter) > 0:
                last_read_chat = filter[-1].chat_id.id

            # lastest chat for case
            chat_room = obj.cases_chatrooms.all()
            filter_chat_room = [
                x for x in chat_room if x.user == case_user and x.agent == agent
            ]

            chat_id = 0

            if len(filter_chat_room) > 0:
                chat_room = filter_chat_room[-1]
                chat = chat_room.chatroom_chats.all()
                chat = chat[len(chat) - 1] if chat else None

                if chat:
                    chat_id = chat.id
                    data["message"] = chat.message
                    data["sent_by"] = chat.sender.email
                    data["sent_date"] = chat.created_at

            if chat_id > last_read_chat:
                data["new_message"] = True
                return data
            else:
                return data

        except Exception as err:
            log_error(
                LOGGER_MODERATE_SEVERITY,
                "UnreadChats:check_for_unread_chats",
                agent,
                description=str(err),
            )
            return "An error occured, check logs for details"

    def create_from_payment(self, customer_id, plan_id):
        agent = User.objects.filter(is_active=True, user_type=User.RCIC).first()
        user = User.objects.get(pk=customer_id)
        plan = Plan.objects.get(pk=plan_id)
        return self.create(user=user, plan=plan, agent=agent)

    def update_plan_agent(self, case_id, plan_id):
        case_modle_obj = self.select_for_update().get(pk=case_id)
        case_modle_obj.agent = User.objects.filter(
            is_active=True, user_type=User.RCIC
        ).first()
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
        (BOOKED, "BOOKED"),
        (IN_PROGRESS, "IN_PROGRESS"),
        (COMPLETED, "COMPLETED"),
        (CANCELLED, "CANCELLED"),
    )

    case_id = models.CharField(max_length=255, primary_key=True)
    display_id = models.CharField(max_length=5, default=None, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.deletion.DO_NOTHING, related_name="users_cases"
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.deletion.DO_NOTHING,
        related_name="agents_cases",
        null=True,
        blank=True,
    )
    account_manager = models.ForeignKey(
        User,
        on_delete=models.deletion.DO_NOTHING,
        related_name="account_manager_cases",
        null=True,
        blank=True,
        default=None,
    )
    status = models.PositiveSmallIntegerField(
        choices=CASES_TYPE_CHOICES, verbose_name="case_status", default=BOOKED
    )
    is_active = models.BooleanField(verbose_name="Active", default=True)
    ref_id = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.deletion.DO_NOTHING
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.deletion.DO_NOTHING, related_name="plans_cases"
    )
    # new program field
    program = models.CharField(max_length=512, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.case_id:
            self.case_id = uuid.uuid4()
        if not self.display_id:
            reverse_case_id = str(self.case_id)[::-1]
            self.display_id = (reverse_case_id[0:5])[::-1]
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.case_id)

    objects = CaseManager()


class Program(TimeStampedModel, SoftDeleteModel):

    EXPRESS_ENTRY = "Express Entry"
    PROVINCIAL_NOMINATION = "Provincial Nomination"
    INVESTORS = "Investors"
    FAMILY_SPONSORSHIP = "Family Sponsorship"

    CHOICES_CATEGORY = (
        (EXPRESS_ENTRY, "EXPRESS_ENTRY"),
        (PROVINCIAL_NOMINATION, "PROVINCIAL_NOMINATION"),
        (INVESTORS, "INVESTORS"),
        (FAMILY_SPONSORSHIP, "FAMILY_SPONSORSHIP"),
    )

    choice = models.CharField(max_length=512, default=None, blank=True, null=True)
    category = models.CharField(
        max_length=512, choices=CHOICES_CATEGORY, default=EXPRESS_ENTRY
    )

    def __str__(self) -> str:
        return self.choice


class AgentNotes(TimeStampedModel, SoftDeleteModel):

    agent = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="agent_notes",
        default=None,
        null=True,
        blank=True,
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.DO_NOTHING,
        default=None,
        null=True,
        related_name="agent_case_notes",
    )
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    notes = models.TextField(default=None, blank=True, null=True)


class CaseCheckPoint(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255, default=None, blank=True, null=True)
    description = models.TextField(default=None, blank=True, null=True)


class CaseTracker(TimeStampedModel, SoftDeleteModel):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3

    CASE_TRACKER_TYPE_CHOICES = (
        (PENDING, "PENDING"),
        (IN_PROGRESS, "IN_PROGRESS"),
        (COMPLETED, "COMPLETED"),
    )

    case_id = models.ForeignKey(
        Case,
        on_delete=models.DO_NOTHING,
        related_name="case_tracker",
        default=None,
        null=True,
        blank=True,
    )
    case_checkpoint = models.ForeignKey(
        CaseCheckPoint,
        on_delete=models.DO_NOTHING,
        related_name="case_checkpoint",
        default=None,
        null=True,
        blank=True,
    )
    status = models.PositiveSmallIntegerField(
        choices=CASE_TRACKER_TYPE_CHOICES, default=PENDING
    )
    comments = models.CharField(max_length=255, default=None, blank=True, null=True)
    index = models.IntegerField(default=None, null=True, blank=True)
