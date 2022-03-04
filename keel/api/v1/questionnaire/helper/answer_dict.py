from keel.questionnaire.models import Question, SpouseQuestion


class AnswerDict(object):
    def __init__(self):
        pass

    def create_answer_dict(self):
        applicant_queryset = Question.objects.all().order_by("id")
        spouse_queryset = SpouseQuestion.objects.all().order_by("id")
        answer_dict = {}

        for question in applicant_queryset:
            answer_dict[question.id] = {}
            answer_dict[question.id]["answer_text_choice_checkbox"] = [
                {
                    i.id: {
                        "with_spouse_score": i.with_spouse_score,
                        "without_spouse_score": i.without_spouse_score,
                    }
                }
                for i in question.question_checkbox.all()
            ]
            answer_dict[question.id]["answer_text_choice_dropdown"] = [
                {
                    i.id: {
                        "with_spouse_score": i.with_spouse_score,
                        "without_spouse_score": i.without_spouse_score,
                    }
                }
                for i in question.question_dropdown.all()
            ]

        # for question in spouse_queryset:
        #     answer_dict[question.id] = {}
        #     answer_dict[question.id]["spouse_question_text"] = question.question_text
        #     answer_dict[question.id]["spouse_answer_type"] = question.answer_type
        #     answer_dict[question.id][
        #         "spouse_answer_type_value"
        #     ] = question.get_answer_type_display()
        #     answer_dict[question.id]["spouse_answer_text"] = ""
        #     answer_dict[question.id]["spouse_answer_text_choice_checkbox"] = [
        #         {i.id: i.score} for i in question.spouse_question_checkbox.all()
        #     ]
        #     answer_dict[question.id]["spouse_answer_text_choice_dropdown"] = [
        #         {i.id: i.score} for i in question.spouse_question_dropdown.all()
        #     ]
        print(ans)
        return answer_dict