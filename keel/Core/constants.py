LOGGER_LOG_MESSAGE="MESSAGE"
LOGGER_LOW_SEVERITY = "LOW"
LOGGER_MODERATE_SEVERITY = "MODERATE"
LOGGER_CRITICAL_SEVERITY = "CRITICAL"

GENERIC_ERROR = "Server Failed to Complete request. Please try again later"

#profile constants
STUDY = 1
PGWP = 2
WORKPERMIT = 3
PR = 4
DEPENDANT = 5
VISIT = 6
CITIZENSHIP = 7

SINGLE = 1
MARRIED = 2
DIVORCED = 3

MARITAL_TYPE = (
    (SINGLE, 'Single'), (MARRIED, 'Married'), (DIVORCED, 'Divorced'),
)

VISA_TYPE = (
    (STUDY, 'Study'), (PGWP, 'PGWP'), (WORKPERMIT, 'WorkPermit'),
    (PR, 'PR'), (DEPENDANT, 'Dependant'), (VISIT, 'Visit'), (CITIZENSHIP, 'Citizenship'),
)

SELF = 'self'
SPOUSE = 'spouse'

OWNER_TYPE = (
    (SELF, 'SELF'), (SPOUSE, 'SPOUSE')
)