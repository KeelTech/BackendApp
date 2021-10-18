"""
This file contains all defaults objects to be returned
for profile api if not instance is found in the databse
"""

PROFILE = {
    "first_name": {"value": "", "type": "char", "labels": "First Name"},
    "last_name": {"value": "", "type": "char", "labels": "Last Name"},
    "date_of_birth": {"value": None, "type": "char", "labels": "Date of Birth"},
    "age": {"value": "", "type": "char", "labels": "Age"},
    "phone_number": {"value": "", "type": "char", "labels": "Phone Number"},
    "mother_fullname": {"value": "", "type": "char", "labels": "Mother's Fullname"},
    "father_fullname": {"value": "", "type": "char", "labels": "Father's Fullname"},
    "current_country": {"value": "", "type": "drop-down", "labels": "Current Country"},
    "desired_country": {"value": "", "type": "drop-down", "labels": "Desired Country"},
    "address": {"value": "", "type": "char", "labels": "Address"},
}

QUALIFICATION = [{
    "institute": {"value": "", "type": "char", "labels": "Institute"},
    "degree": {"value": "", "type": "char", "labels": "Degree"},
    "year_of_passing": {"value": "", "type": "int", "labels": "Year Of Passing"},
    "grade": {"value": "", "type": "char", "labels": "Grade"},
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
    "start_date": {"value": None, "type": "char", "labels": "Start Date"},
    "end_date": {"value": None, "type": "char", "labels": "End Date"},
}]

ECA = [{
    "eca_authority_name": {"value": "", "type": "char", "labels": "ECA Authority Name"},
    "eca_authority_number": {"value": "", "type": "char", "labels": "ECA Authority Number"},
    "canadian_equivalency_summary": {"value": "", "type": "char", "labels": "Canadian Equivalency Summary"},
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

WORK_EXPERIENCE = [{
    "company_name": {"value": "", "type": "char", "labels": "Company Name"},
    "designation": {"value": "", "type": "char", "labels": "Desgination"},
    "job_type": {"value": "", "type": "char", "labels": "Job Type"},
    "job_description": {"value": "", "type": "char", "labels": "Job Description"},
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