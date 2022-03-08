from keel.api.v1.questionnaire.helper import answer_dict
from keel.questionnaire.models import Question
from keel.api.v1.questionnaire.helper.answer_dict import AnswerDict

answer_dict = AnswerDict()


class CrsCalculatorWithoutSpouse(object):
    def __init__(self, data={}):
        self.data = data

    def fetch_score_from_database(self, question, answer):
        score = 0
        try:
            score = (
                Question.objects.filter(id=question)
                .first()
                .question_dropdown.filter(id=answer)
                .first()
                .without_spouse_score
            )
        except Exception as e:
            pass
        print("Score: ", score)
        return int(score)
    
    def calc_score(self):
        score = 0
        
        for key, value in self.data.items():
            
            if type(value) is dict:
                question_id = value['question_id']
                answer_id = value['answer_id']
                score += self.fetch_score_from_database(question_id, answer_id)
            else:
                pass
        
        return score