import logging
from rest_framework import serializers
from keel.cases.models import Case, Program
from keel.Core.err_log import log_error
from keel.api.v1.auth.serializers import UserDetailsSerializer

logger = logging.getLogger('app-logger')

class CasesSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source="user.email")
    # agent = serializers.ReadOnlyField(source="agent.email")
    plan = serializers.SerializerMethodField()
    user_details = UserDetailsSerializer(source = 'user',many = False)

    class Meta:
        model = Case
        fields = ('case_id', 'display_id', 'user', 'agent', 'account_manager_id', 'ref_id', 
                    'plan', 'status', 'is_active', 'program', 'created_at', 'updated_at','user_details')
    
    def get_plan(self, obj):
        return {'id':obj.plan.id, 'name':obj.plan.title}

class CaseIDSerializer(serializers.Serializer):

    case_id = serializers.CharField(max_length = 255)
    user_id = serializers.CharField(max_length = 255, required = False)

    def validate(self, attrs):

        case_obj = ''
        case_id = attrs.get("case_id")
        if not case_id:
            raise serializers.ValidationError("Invalid Case Id passed")

        try:
            case_obj = Case.objects.get(pk = case_id, deleted_at__isnull = True)
        except Case.DoesNotExist as e:
            log_error("ERROR", "CaseIDSerializer: validate", "", err = str(e), case_id = case_id)
            raise serializers.ValidationError("Case Id does not exist")

        if attrs.get("user_id"):
            user_id = attrs.get("user_id")
            # If user_id is present, check user_id against the case User/Agent.
            # if not matching raise Case Invalid Error
            if not (str(case_obj.user_id) == user_id or str(case_obj.agent_id) == user_id):
                log_error("ERROR","CaseIDSerializer: validate", str(user_id), err = "Case Id does not match with User", case_id = case_id)
                raise serializers.ValidationError("Case Id does not exist")

        return case_obj

class BaseCaseProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = ('id', 'choice', 'category')

class CaseProgramSerializer(serializers.Serializer):
    program = serializers.CharField()

    def validate(self, attrs):
        program = attrs.get('program')

        if program is None:
            raise serializers.ValidationError("Please input a valid program option")
        
        # validate program in Program model
        try:
            check_program = Program.objects.get(choice=program)
        except Program.DoesNotExist as e:
            logger.error('ERROR: CASE:FilterUserCasesDetails ' + str(e))
            raise serializers.ValidationError("Program matching query does not exist")
        
        return program