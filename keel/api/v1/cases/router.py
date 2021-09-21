from django.urls import path
from .views import (FilterUserCases, FilterUserCasesDetails, CaseView, 
                    UpdateCaseProgramView)

urlpatterns = [
    path('create-cases', CaseView.as_view(), name="create-case"),
    path('list-cases', FilterUserCases.as_view(), name='list-cases'),
    path('list-case-programs', UpdateCaseProgramView.as_view({'get':'get_all_programs'}),  name='get-all-programs'),
    path('update-program/<str:case_id>', UpdateCaseProgramView.as_view({'post':'update_program'}), name='update-program'),
    path('list-cases-details/<str:case_id>', FilterUserCasesDetails.as_view({'get':'get_case'}), name='list-cases-details'),
]
