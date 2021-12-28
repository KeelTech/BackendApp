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

    def calculate_crs_without_spouse(self):
        data = self.data

        # calculate applicants age
        age_question = int(data.get("age", None).get("question_id", None))
        age_answer = int(data.get("age", None).get("answer_id", None))
        get_age_score = self.fetch_score_from_database(age_question, age_answer)

        # calculate applicant education
        education_question = int(data["education"].get("question_id", None))
        education_answer = int(data["education"].get("answer_id", None))
        get_education_score = self.fetch_score_from_database(
            education_question, education_answer
        )

        # work experience
        work_experience_question = int(data["work_experience"].get("question_id", None))
        work_experience_answer = int(data["work_experience"].get("answer_id", None))
        get_work_experience_score = self.fetch_score_from_database(
            work_experience_question, work_experience_answer
        )

        # first language speaking
        first_language_speaking_answer = int(
            data["first_language_speaking"].get("answer_id", None)
        )
        first_language_speaking_question = int(
            data["first_language_speaking"].get("question_id", None)
        )
        get_first_language_speaking_score = self.fetch_score_from_database(
            first_language_speaking_question, first_language_speaking_answer
        )

        # first language reading
        first_language_reading_answer = int(
            data["first_language_reading"].get("answer_id", None)
        )
        first_language_reading_question = int(
            data["first_language_reading"].get("question_id", None)
        )
        get_first_language_reading_score = self.fetch_score_from_database(
            first_language_reading_question, first_language_reading_answer
        )

        # first language writing
        first_language_writing_answer = int(
            data["first_language_writing"].get("answer_id", None)
        )
        first_language_writing_question = int(
            data["first_language_writing"].get("question_id", None)
        )
        get_first_language_writing_score = self.fetch_score_from_database(
            first_language_writing_question, first_language_writing_answer
        )

        # first language listening
        first_language_listening_answer = int(
            data["first_language_listening"].get("answer_id", None)
        )
        first_language_listening_question = int(
            data["first_language_listening"].get("question_id", None)
        )
        get_first_language_listening_score = self.fetch_score_from_database(
            first_language_listening_question, first_language_listening_answer
        )

        get_language_score = (
            get_first_language_listening_score
            + get_first_language_reading_score
            + get_first_language_speaking_score
            + get_first_language_writing_score
        )

        return (
            get_language_score
            + get_age_score
            + get_work_experience_score
            + get_education_score
        )
