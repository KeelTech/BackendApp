from keel.questionnaire.models import Question, SpouseQuestion


class CrsCalculatorWithSpouse(object):
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
                .with_spouse_score
            )
        except Exception as e:
            pass

        return int(score)

    def fetch_spouse_score_from_database(self, question, answer):
        score = 0
        try:
            score = (
                SpouseQuestion.objects.filter(id=question)
                .first()
                .spouse_question_dropdown.filter(id=answer)
                .first()
                .with_spouse_score
            )
        except Exception as e:
            pass
        return int(score)

    def calculate_crs_with_spouse(self):
        data = self.data

        # applicant age
        age_question = int(data.get("age", None).get("question_id", None))
        age_answer = int(data.get("age", None).get("answer_id", None))
        get_age_score = self.fetch_score_from_database(age_question, age_answer)

        # applicant education
        education_question = int(data["education"].get("question_id", None))
        education_answer = int(data["education"].get("answer_id", None))
        get_education_score = self.fetch_score_from_database(
            education_question, education_answer
        )

        # applicant work experience
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

        # second language speaking
        second_language_speaking_answer = int(
            data["second_language_speaking"].get("answer_id", None)
        )
        second_language_speaking_question = int(
            data["second_language_speaking"].get("question_id", None)
        )
        get_second_language_speaking_score = self.fetch_score_from_database(
            second_language_speaking_question, second_language_speaking_answer
        )

        # second language reading
        second_language_reading_answer = int(
            data["second_language_reading"].get("answer_id", None)
        )
        second_language_reading_question = int(
            data["second_language_reading"].get("question_id", None)
        )
        get_second_language_reading_score = self.fetch_score_from_database(
            second_language_reading_question, second_language_reading_answer
        )

        # second language writing
        second_language_writing_answer = int(
            data["second_language_writing"].get("answer_id", None)
        )
        second_language_writing_question = int(
            data["second_language_writing"].get("question_id", None)
        )
        get_second_language_writing_score = self.fetch_score_from_database(
            second_language_writing_question, second_language_writing_answer
        )

        # second language listening
        second_language_listening_answer = int(
            data["second_language_listening"].get("answer_id", None)
        )
        second_language_listening_question = int(
            data["second_language_listening"].get("question_id", None)
        )
        get_second_language_listening_score = self.fetch_score_from_database(
            second_language_listening_question, second_language_listening_answer
        )

        # spouse education
        spouse_education_question = int(
            data["spouse_education"].get("question_id", None)
        )
        spouse_education_answer = int(data["spouse_education"].get("answer_id", None))
        get_spouse_education_score = self.fetch_spouse_score_from_database(
            spouse_education_question, spouse_education_answer
        )

        # spouse work experience
        spouse_work_experience_question = int(
            data["spouse_work_experience"].get("question_id", None)
        )
        spouse_work_experience_answer = int(
            data["spouse_work_experience"].get("answer_id", None) 
        )
        get_spouse_work_experience_score = self.fetch_spouse_score_from_database(
            spouse_work_experience_question, spouse_work_experience_answer
        )

        # spouse language speaking
        spouse_language_speaking_answer = int(
            data["spouse_language_speaking"].get("answer_id", None)
        )
        spouse_language_speaking_question = int(
            data["spouse_language_speaking"].get("question_id", None)
        )
        get_spouse_language_speaking_score = self.fetch_spouse_score_from_database(
            spouse_language_speaking_question, spouse_language_speaking_answer
        )

        # spouse language reading
        spouse_language_reading_answer = int(
            data["spouse_language_reading"].get("answer_id", None)
        )
        spouse_language_reading_question = int(
            data["spouse_language_reading"].get("question_id", None)
        )
        get_spouse_language_reading_score = self.fetch_spouse_score_from_database(
            spouse_language_reading_question, spouse_language_reading_answer
        )

        # spouse language writing
        spouse_langugage_writing_answer = int(
            data["spouse_language_writing"].get("answer_id", None)
        )
        spouse_langugage_writing_question = int(
            data["spouse_language_writing"].get("question_id", None)
        )
        get_spouse_language_writing_score = self.fetch_spouse_score_from_database(
            spouse_langugage_writing_question, spouse_langugage_writing_answer
        )

        # spouse language listening
        spouse_langugage_listening_answer = int(
            data["spouse_language_listening"].get("answer_id", None)
        )
        spouse_langugage_listening_question = int(
            data["spouse_language_listening"].get("question_id", None)
        )
        get_spouse_langugage_listening_score = self.fetch_spouse_score_from_database(
            spouse_langugage_listening_question, spouse_langugage_listening_answer
        )

        get_total_language_score = (
            (
                get_first_language_writing_score
                + get_first_language_reading_score
                + get_first_language_listening_score
                + get_first_language_speaking_score
            )
            + (
                get_second_language_reading_score
                + get_second_language_listening_score
                + get_second_language_speaking_score
                + get_second_language_writing_score
            )
            + (
                get_spouse_language_reading_score
                + get_spouse_language_writing_score
                + get_spouse_langugage_listening_score
                + get_spouse_language_speaking_score
            )
        )

        get_total_education_score = get_education_score + get_spouse_education_score

        get_total_work_experience_score = (
            get_work_experience_score + get_spouse_work_experience_score
        )

        return (
            get_total_language_score
            + get_total_education_score
            + get_total_work_experience_score
            + get_age_score
        )
