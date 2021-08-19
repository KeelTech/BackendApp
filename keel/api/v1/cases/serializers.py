from rest_framework import serializers
from keel.cases.models import Case
from keel.Core.err_log import log_error


class CasesSerializer(serializers.ModelSerializer):

    plan = serializers.ReadOnlyField(source="plan.title")
    
    class Meta:
        model = Case
        fields = ('case_id', 'display_id', 'user', 'agent', 'account_manager_id', 'ref_id', 
                    'plan', 'status', 'is_active', 'created_at', 'updated_at')

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
            log_error("ERROR", "CaseIDSerializer: validate", "", str(e), case_id = case_id)
            raise serializers.ValidationError("Case Id does not exist")

        if attrs.get("user_id"):
            user_id = attrs.get("user_id")
            # If user_id is present, check user_id against the case User/Agent.
            # if not matching raise Case Invalid Error
            if not (str(case_obj.user_id) == user_id or str(case_obj.agent_id) == user_id):
                log_error("ERROR","CaseIDSerializer: validate", str(user_id), err = "Case Id does not match with User", case_id = case_id)
                raise serializers.ValidationError("Case Id does not exist")

        return case_obj




