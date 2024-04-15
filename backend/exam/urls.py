from django.contrib import admin
from django.urls import path


from .views.coursemanagementviews import (
    ChoicesView,
    CourseStructureView,
    CourseView,
    ManageCourseView,
    QuestionView,
    QuizView,
    ReadingMaterialView,
)

from .views.courseviews import (
    QuizTake,
    dummy_quiz_index,
)
from .views.registercourseviews import (
    CourseCustomerRegistrationView,
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
    LMSCustomerListView,
    CreateCourseRegisterRecordView,
    ManageCourseRegistrationRecordStatusView,
)
from .views.enrollcourseviews import (
    RegisteredCourseListView,
    UserListForEnrollmentView,
    CreateCourseEnrollmentView,
    DisplayCourseEnrollmentView,
    UnAssignCourseEnrollmentView,
    AssignCourseEnrollmentView
)

urlpatterns = [

    #courseview.py  views url
    path("<int:pk>/<slug:quiz_slug>/take/", QuizTake.as_view(), name="quiz_take"), #href="{% url 'quiz_take' pk=course.pk slug=quiz.slug %}
    #extra
    path('quiz/redirect/<int:course_id>/', view=dummy_quiz_index, name='quiz_index'),
    
    
    #registercourseviews.py views url
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'),
    path('course-register-record/', CourseCustomerRegistrationView.as_view(), name='course-register-record'),
    path('manage-status/register-records/', ManageCourseRegistrationRecordStatusView.as_view(), name='manage-register-records'), 
    path('create/course-register-record/', CreateCourseRegisterRecordView.as_view(), name='create-course-register-record'),

    #coursemanagementviews.py views url
    path('courses/', CourseView.as_view(), name='courses'), #*
    path('manage/course/', ManageCourseView.as_view(), name='manage-course'), #*
    path('course/<int:course_id>/structure/', CourseStructureView.as_view(), name='course-structure'), #*
    path('course/<int:course_id>/reading-material/', ReadingMaterialView.as_view(), name='reading-material'), #*
    path('quiz/<int:quiz_id>/question/', QuestionView.as_view(), name='reading-material'), #*
    path('course/<int:course_id>/quiz/', QuizView.as_view(), name='quiz'), #*
    path('question/<int:question_id>/choices/', ChoicesView.as_view(), name='question-choice'),
    
    #enrollcourseviews.py views url
    path('display/registered-course/', RegisteredCourseListView.as_view(), name='register-course-list'),
    path('display/users/', UserListForEnrollmentView.as_view(), name='users-list'),
    path('create/course-enrollments/', CreateCourseEnrollmentView.as_view(), name='create-course-enrollments-record'),
    path('display/course-enrollments/', DisplayCourseEnrollmentView.as_view(), name='course-enrollments-list'),
    path('enrollments/unassign/', UnAssignCourseEnrollmentView.as_view(), name='unassign-course-enrollment'),
    path('enrollments/assign/', AssignCourseEnrollmentView.as_view(), name='assign-course-enrollment')
    
]
