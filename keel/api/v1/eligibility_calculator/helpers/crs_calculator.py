import score_dict


class CrsCalculator(object):
    """
    Class to calculate the CRS score.
    """

    def __init__(self, is_with_spouse, education, age, language_test, work_experience):
        
        self.is_with_spouse = is_with_spouse
        self.education = education
        self.age = age
        self.language_test = language_test
        self.work_experience = work_experience

    def calculate_crs_with_spouse(self):
        """
        Calculate the CRS score with spouse.
        """

        # EDUCATION
        education_applicant = score_dict.EDUCATION_LEVEL_WITH_SPOUSE['PRINCIPAL_APPLICANT'].get(self.education)
        education_spouse = score_dict.EDUCATION_LEVEL_WITH_SPOUSE['SPOUSE'].get(self.education)
        # LANGUAGE
        language_test_applicant = score_dict.FIRST_LANGUAGE_PROFICIENCY_WITH_SPOUSE['PRINCIPAL_APPLICANT'].get(self.language_test)
        language_test_spouse = score_dict.FIRST_LANGUAGE_PROFICIENCY_WITH_SPOUSE['SPOUSE'].get(self.language_test)
        # WORK EXPERIENCE
        work_experience_applicant = score_dict.WORK_EXPERIENCE_WITH_SPOUSE['PRINCIPAL_APPLICANT'].get(self.work_experience)
        work_experience_spouse = score_dict.WORK_EXPERIENCE_WITH_SPOUSE['SPOUSE'].get(self.work_experience)

        # each of this variables should return an integer
        get_education = education_applicant + education_spouse
        get_language_test = (language_test_applicant * 4) + language_test_spouse
        get_age = score_dict.AGE_WITHOUT_SPOUSE.get(self.age)
        get_work_experience = work_experience_applicant + work_experience_spouse

        # perform calculation with addition operation
        crs_score = (get_education + get_language_test + get_age + get_work_experience)

        return crs_score
    
    def calculate_crs_without_spouse(self):
        """
        Calculate the CRS score without spouse.
        """
        
        # each of this variables should return an integer
        get_education = score_dict.EDUCATION_LEVEL_WITHOUT_SPOUSE.get(self.education, None)
        get_language_test = (score_dict.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE.get(self.language_test, None) * 4 )
        get_age = score_dict.AGE_WITHOUT_SPOUSE.get(self.age, None)
        get_work_experience = score_dict.WORK_EXPERIENCE_WITHOUT_SPOUSE.get(self.work_experience, None)

        # perform calculation with addition operation
        crs_score = (get_education + get_language_test + get_age + get_work_experience)

        return crs_score