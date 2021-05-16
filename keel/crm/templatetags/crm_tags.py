import datetime
from django import template

from keel.crm.constants import constants
from django.contrib.auth.models import Group
from keel.authentication.models import QCModel

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name).first()
    if group and group in user.groups.all():
        return True
    else:
        return False

@register.inclusion_tag('custom_submit.html',takes_context=True)
def show_actions(context, original):
    # dict = {'Submit for QA Check':'_qa_submit','Approve QA Check' : '_qa_approve'}
    # return {'choices': dict}
    data_status = 0
    if(original):
        data_status = original.data_status

    request = context.request
    available_actions = {'_submit_for_qc':'Submit for Quality Check','_qc_approve':'Approve Quality Check','_mark_in_progress':'Reject Quality Check'}
    actions = {}

    if (request.user.is_superuser and request.user.is_staff) or request.user.is_member_of(constants['SUPER_QC_GROUP']):
        actions['_submit_for_qc'] = available_actions['_submit_for_qc']
        actions['_qc_approve'] = available_actions['_qc_approve']
        actions['_mark_in_progress'] = available_actions['_mark_in_progress']

    # check if member of QC Team
    if request.user.is_member_of(constants['QC_GROUP_NAME']):
        # if data_status == QCModel.IN_PROGRESS:
        #     actions['_submit_for_qc'] = available_actions['_submit_for_qc']
        # elif data_status == QCModel.SUBMITTED_FOR_QC:
        if data_status == QCModel.SUBMITTED_FOR_QC:
            actions['_qc_approve'] = available_actions['_qc_approve']
            actions['_mark_in_progress'] = available_actions['_mark_in_progress']

    # if field team member
    if request.user.is_member_of(constants['DOCTOR_NETWORK_GROUP_NAME']):
        if data_status == QCModel.IN_PROGRESS or data_status == QCModel.REOPENED:
            actions['_submit_for_qc'] = available_actions['_submit_for_qc']

    if request.user.is_member_of(constants['WELCOME_CALLING_TEAM']):
        if data_status == QCModel.QC_APPROVED:
            actions['_mark_in_progress'] = available_actions['_mark_in_progress']

    return {'choices': actions}


@register.inclusion_tag('custom_submit.html', takes_context=True)
def custom_test(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
