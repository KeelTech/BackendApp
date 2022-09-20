"""
This file contains all defaults objects to be returned
for profile api if not instance is found in the databse
"""
from keel.authentication.models import CustomerLanguageScore, CustomerProfile, CustomerFamilyInformation

PROFILE = {
    "first_name": {"value": "", "type": "char", "labels": "First Name"},
    "last_name": {"value": "", "type": "char", "labels": "Last Name"},
    "date_of_birth": {"value": None, "type": "char", "labels": "Date of Birth"},
    "age": {"value": "", "type": "char", "labels": "Age"},
    "phone_number": {"value": "", "type": "char", "labels": "Phone Number"},
    "mother_fullname": {"value": "", "type": "char", "labels": "Mother's Fullname"},
    "father_fullname": {"value": "", "type": "char", "labels": "Father's Fullname"},
    "type_of_visa": {"value": "", "type": "drop-down", "choices": CustomerProfile.VISA_TYPE, "labels": "Type of Visa"},
    "current_country": {"value": 1, "type": "drop-down", "labels": "Current Country"},
    "desired_country": {"value": 1, "type": "drop-down", "labels": "Desired Country"},
    "address": {"value": "", "type": "char", "labels": "Address"},
}

SPOUSEPROFILE = {
    "first_name": {"value": "", "type": "char", "labels": "First Name"},
    "last_name": {"value": "", "type": "char", "labels": "Last Name"},
    "age": {"value": "", "type": "char", "labels": "Age"},
    "date_of_marriage": {"value": "", "type": "calendar", "labels": "Date of Marriage"},
    "number_of_children": {"value": "", "type": "int", "labels": "Number of Children"},
    "mother_fullname": {"value": "", "type": "char", "labels": "Mother's Fullname"},
    "father_fullname": {"value": "", "type": "char", "labels": "Father's Fullname"},
    "passport_number": {"value": "", "type": "char", "labels": "Passport Number"},
    "passport_country": {"value": 1, "type": "drop-down", "labels": "passport Country"},
    "passport_issue_date": {"value": "", "type": "calendar", "labels": "Passport Issue Date"},
    "passport_expiry_date": {"value": "", "type": "calendar", "labels": "Passport Expiry Date"},
}

CUSTOMERFAMILYINFO = [{
    "relationship": {"value": "", "type": "drop-down", "labels": "Relationship", "choices": CustomerFamilyInformation.RELATION_TYPE,},
    "first_name": {"value": "", "type": "char", "labels": "First Name"},
    "last_name": {"value": "", "type": "char", "labels": "Last Name"},
    "date_of_birth": {"value": "", "type": "calendar", "labels": "Date of Birth"},
    "date_of_death": {"value": "", "type": "calendar", "labels": "Date of Death", "is_optional": True},
    "city_of_birth": {"value": "", "type": "char", "labels": "City of Birth"},
    "country_of_birth": {"value": 1, "type": "drop-down", "labels": "Country of Birth"},
    "street_address": {"value": "", "type": "char", "labels": "Street Address"},
    "current_country": {"value": 1, "type": "drop-down", "labels": "Current Country"},
    "current_state": {"value": 1, "type": "drop-down", "labels": "Current State"},
    "current_occupation": {"value": "", "type": "char", "labels": "Current Occupation"},
}]

QUALIFICATION = [{
    "institute": {"value": "", "type": "char", "labels": "Institute"},
    "degree": {"value": "", "type": "char", "labels": "Degree"},
    "year_of_passing": {"value": "", "type": "int", "labels": "Year Of Passing"},
    "grade": {"value": "", "type": "char", "labels": "Grade"},
    "country": {"value": "", "type": "char", "labels": "Country"},
    "state": {"value": "", "type": "char", "labels": "State"},
    "city": {"value": "", "type": "char", "labels": "City"},
    "full_address": {
        "type": 'address', 
        "countryLabel":"Country", 
        "country": "",
        "countryId": "", 
        "stateLabel":"State", 
        "state": "",
        "stateId": "",
        "cityLabel":"City",
        "city": "",
        "cityId": ""
    },
    "start_date": {"value": None, "type": "char", "labels": "Start Date"},
    "end_date": {"value": None, "type": "char", "labels": "End Date"},
}]

ECA = [{
    "eca_authority_name": {"value": "", "type": "char", "labels": "ECA Authority Name"},
    "eca_authority_number": {"value": "", "type": "char", "labels": "ECA Authority Number"},
    "canadian_equivalency_summary": {"value": "", "type": "char", "labels": "Canadian Equivalency Summary"},
    "eca_date": {"value": "", "type": "calendar", "labels": "ECA Date"},
}]

RELATIVE = {
    "full_name": {"value": "", "type": "char", "labels": "Full Name"},
    "relationship": {"value": "", "type": "char", "labels": "Relationship"},
    "immigration_status": {"value": "", "type": "char", "labels": "Immigration Status"},
    "address": {"value": "", "type": "char", "labels": "Address"},
    "contact_number": {"value": "", "type": "char", "labels": "Contact Number"},
    "email_address": {"value": "", "type": "char", "labels": "Email Address"},
    "is_blood_relationship" : {"value": False, "type":"checkbox", "labels":"Is Blood Relationship"}
}

LANGUAGESCORE = [{
    "test_type": {"value": "", "choices": CustomerLanguageScore.TEST_TYPE, "type": "drop-down", "labels": "Test Type"},
    "test_version": {"value": "", "type": "char", "labels": "Test Version"},
    "result_date": {"value": "", "type": "calendar", "labels": "Result Date"},
    "test_date": {"value": "", "type": "calendar", "labels": "Test Date"},
    "report_form_number": {"value": "", "type": "char", "labels": "Test Report Form Number"},
    "listening_score": {"value": "", "type": "char", "labels": "Listening Score"},
    "writing_score": {"value": "", "type": "char", "labels": "Writing Score"},
    "speaking_score": {"value": "", "type": "char", "labels": "Speaking Score"},
    "reading_score": {"value": "", "type": "char", "labels": "Reading Score"},
    "overall_score": {"value": "", "type": "char", "labels": "Overall Score"},
}]

WORK_EXPERIENCE = [{
    "company_name": {"value": "", "type": "char", "labels": "Company Name"},
    "designation": {"value": "", "type": "char", "labels": "Desgination"},
    "job_type": {"value": "", "type": "char", "labels": "Job Type"},
    "job_description": {"value": "", "type": "textarea", "labels": "Job Description"},
    "weekly_working_hours": {"value": "", "type": "char", "labels": "Weekly Working Hours"},
    "start_date": {"value": None, "type": "char", "labels": "Start Date"},
    "end_date": {"value": None, "type": "char", "labels": "End Date"},
    "country": {"value": "", "type": "char", "labels": "Country"},
    "state": {"value": "", "type": "char", "labels": "State"},
    "city": {"value": "", "type": "char", "labels": "City"},
    "full_address" : { 
        "type": 'address', 
        "countryLabel":"Country", 
        "country": "",
        "countryId": "", 
        "stateLabel":"State", 
        "state": "",
        "stateId": "",
        "cityLabel":"City",
        "city": "",
        "cityId": ""
    },
}]