from . import score_dict_with_spouse, score_dict_without_spouse, additional_points


class CrsCalculator(object):
    """
    Class to calculate the CRS score.
    """

    def __init__(
        self,
        age,
        education,
        language,
        work_experience,
        spouse_details,
        arranged_employement,
        relative_in_canada,
        provincial_nomination,
    ):

        self.education = education
        self.age = age
        self.language = language
        self.work_experience = work_experience
        self.spouse_details = spouse_details
        self.arranged_employement = arranged_employement
        self.relative_in_canada = relative_in_canada
        self.provincial_nomination = provincial_nomination

    def calculate_crs_with_spouse(self):
        """
        Calculate the CRS score with spouse.
        """

        # EDUCATION
        education_applicant = score_dict_with_spouse.APPLICANT_EDUCATION_LEVEL.get(
            self.education, 0
        )
        spouse_edu = self.spouse_details.get("spouse_education", None)
        education_spouse = score_dict_with_spouse.SPOUSE_EDUCATION_LEVEL.get(
            spouse_edu, 0
        )
        # APPLICANT FIRST AND SECOND LANGUAGE
        first_language_speaking_test_applicant = (
            score_dict_with_spouse.APPLICANT_FIRST_LANGUAGE_PROFICIENCY["Speaking"].get(
                self.language.get("first_language_speaking", ""), 0
            )
        )
        first_language_reading_test_applicant = (
            score_dict_with_spouse.APPLICANT_FIRST_LANGUAGE_PROFICIENCY["Reading"].get(
                self.language.get("first_language_reading", ""), 0
            )
        )
        first_language_writing_test_applicant = (
            score_dict_with_spouse.APPLICANT_FIRST_LANGUAGE_PROFICIENCY["Writing"].get(
                self.language.get("first_language_writing", ""), 0
            )
        )
        first_language_listening_test_applicant = (
            score_dict_with_spouse.APPLICANT_FIRST_LANGUAGE_PROFICIENCY[
                "Listening"
            ].get(self.language.get("first_language_listening", ""), 0)
        )
        second_language_speaking_test_applicant = (
            score_dict_with_spouse.APPLICANT_SECOND_LANGUAGE_PROFICIENCY[
                "Speaking"
            ].get(self.language.get("second_language_speaking", ""), 0)
        )
        second_language_reading_test_applicant = (
            score_dict_with_spouse.APPLICANT_SECOND_LANGUAGE_PROFICIENCY["Reading"].get(
                self.language.get("second_language_reading", ""), 0
            )
        )
        second_language_writing_test_applicant = (
            score_dict_with_spouse.APPLICANT_SECOND_LANGUAGE_PROFICIENCY["Writing"].get(
                self.language.get("second_language_writing", ""), 0
            )
        )
        second_language_listening_test_applicant = (
            score_dict_with_spouse.APPLICANT_SECOND_LANGUAGE_PROFICIENCY[
                "Listening"
            ].get(self.language.get("second_language_listening", ""), 0)
        )

        # SPOUSE LANGUAGE TEST
        spouse_speaking_language_test = (
            score_dict_with_spouse.SPOUSE_LANGUAGE_PROFICIENCY["Speaking"].get(
                self.spouse_details.get("spouse_language_speaking", ""), 0
            )
        )
        spouse_writing_language_test = (
            score_dict_with_spouse.SPOUSE_LANGUAGE_PROFICIENCY["Writing"].get(
                self.spouse_details.get("spouse_language_writing", ""), 0
            )
        )
        spouse_reading_language_test = (
            score_dict_with_spouse.SPOUSE_LANGUAGE_PROFICIENCY["Reading"].get(
                self.spouse_details.get("spouse_language_reading", ""), 0
            )
        )
        spouse_listening_language_test = (
            score_dict_with_spouse.SPOUSE_LANGUAGE_PROFICIENCY["Listening"].get(
                self.spouse_details.get("spouse_language_listening", ""), 0
            )
        )

        # WORK EXPERIENCE
        work_experience_applicant = (
            score_dict_with_spouse.APPLICANT_WORK_EXPERIENCE.get(
                self.work_experience, 0
            )
        )
        work_experience_spouse = score_dict_with_spouse.SPOUSE_WORK_EXPERIENCE.get(
            self.spouse_details.get("spouse_work_experience"), 0
        )

        # AGE
        age = score_dict_with_spouse.AGE.get(self.age, 0)

        # each of this variables should return an integer
        get_education = education_applicant + education_spouse
        get_language_test = (
            (
                first_language_speaking_test_applicant
                + first_language_reading_test_applicant
                + first_language_writing_test_applicant
                + first_language_listening_test_applicant
            )
            + (
                second_language_reading_test_applicant
                + second_language_speaking_test_applicant
                + second_language_writing_test_applicant
                + second_language_listening_test_applicant
            )
            + (
                spouse_reading_language_test
                + spouse_speaking_language_test
                + spouse_writing_language_test
                + spouse_listening_language_test
            )
        )
        get_age = age
        get_work_experience = work_experience_applicant + work_experience_spouse

        # perform calculation with addition operation
        crs_score = get_education + get_language_test + get_age + get_work_experience

        # additionl scores
        additional = self.other_scores()

        return crs_score + additional

    def calculate_crs_without_spouse(self):
        """
        Calculate the CRS score without spouse.
        """

        # EDUCATION
        get_education = score_dict_without_spouse.EDUCATION_LEVEL_WITHOUT_SPOUSE.get(
            self.education, 0
        )

        # FIRST AND SECOND LANGUAGE
        first_language_speaking_test_applicant = (
            score_dict_without_spouse.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Speaking"
            ].get(self.language.get("first_language_speaking", ""), 0)
        )

        first_language_reading_test_applicant = (
            score_dict_without_spouse.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Reading"
            ].get(self.language.get("first_language_reading", ""), 0)
        )
        first_language_writing_test_applicant = (
            score_dict_without_spouse.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Writing"
            ].get(self.language.get("first_language_writing", ""), 0)
        )
        first_language_listening_test_applicant = (
            score_dict_without_spouse.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Listening"
            ].get(self.language.get("first_language_listening", ""), 0)
        )
        second_language_speaking_test_applicant = (
            score_dict_without_spouse.SECOND_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Speaking"
            ].get(self.language.get("second_language_speaking", ""), 0)
        )
        second_language_reading_test_applicant = (
            score_dict_without_spouse.SECOND_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Reading"
            ].get(self.language.get("second_language_reading", ""), 0)
        )
        second_language_writing_test_applicant = (
            score_dict_without_spouse.SECOND_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Writing"
            ].get(self.language.get("second_language_writing", ""), 0)
        )
        second_language_listening_test_applicant = (
            score_dict_without_spouse.SECOND_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE[
                "Listening"
            ].get(self.language.get("second_language_listening", ""), 0)
        )

        get_age = score_dict_without_spouse.AGE_WITHOUT_SPOUSE.get(self.age, 0)

        get_work_experience = (
            score_dict_without_spouse.WORK_EXPERIENCE_WITHOUT_SPOUSE.get(
                self.work_experience, 0
            )
        )

        get_language_test = (
            first_language_listening_test_applicant
            + first_language_reading_test_applicant
            + first_language_speaking_test_applicant
            + first_language_writing_test_applicant
        ) + (
            second_language_listening_test_applicant
            + second_language_reading_test_applicant
            + second_language_speaking_test_applicant
            + second_language_writing_test_applicant
        )

        # perform calculation with addition operation
        crs_score = get_education + get_language_test + get_age + get_work_experience

        # additionl scores
        additional = self.other_scores()

        return crs_score + additional

    def other_scores(self):

        # brother or sister living in canada
        relative = additional_points.BROTHER_IN_CANADA.get(self.relative_in_canada, 0)

        # french skills

        # canada post education

        # arranged employement

        # PN nomination
        provincial_nomination = additional_points.PROVINVIAL_NOMINATION.get(
            self.provincial_nomination, 0
        )

        # print("here", provincial_nomination)

        return provincial_nomination + relative
