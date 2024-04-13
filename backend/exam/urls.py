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

# from .views.userdashboardviews import  ActiveRegisteredCustomerCountView, CountOfActiveRegistrationPerCoure, CourseCountView, GraphOfProgressPerCourseView 
# from .views.editcourseviews import EditCourseInstanceDetailsView, NotificationBasedOnCourseDisplayView
from .views.courseviews import (
    # ActiveCourseListDisplayView,
    # AllCourseListDisplayView,
    # InActiveCourseListDisplayView,
    # CourseInstanceDetailDisplayView,
    # SingleCourseStructureListDisplayView,
    # ReadingMaterialInstanceDisplayView,
    # VideoInstanceDisplayView,
    # QuizInstanceDisplayView,
    QuizTake,
    dummy_quiz_index,
    # ReadingMaterialListPerCourseView,
    # VideoMaterialListPerCourseView,
    # QuizListPerCourseView,
    # QuestionListPerQuizView
)
from .views.registercourseviews import (
    CourseCustomerRegistrationView,
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
    LMSCustomerListView,
    CreateCourseRegisterRecordView,
    # DisplayCourseRegisterRecordView,
    # # DeleteCourseRegisterRecordView,
    # DeleteSingleCourseRegisterRecordInstanceView,
    # DeactivateCourseRegistrationRecordView,
    # ActivateCourseRegistrationRecordView,
    ManageCourseRegistrationRecordStatusView,
    # DisplayActiveCourseRegisterRecordView,
    # DisplayInActiveCourseRegisterRecordView
)
# from .views.enrollcourseviews import (
#     RegisteredCourseListView,
#     UserListForEnrollment,
#     CreateCourseEnrollmentView,
#     DisplayCourseEnrollmentView,
#     UnAssignCourseEnrollmentView,
#     AssignCourseEnrollmentView
# )
# from .views.createcourseviews import (
#     # CreateCourseView,
#     CreateReadingMaterialView,
#     CreateVideoView,
#     CreateQuizView,
#     CreateCourseStructureForCourseView,
#     CreateQuestionView,
#     CreateChoiceView,
#     # ActivateCourseView,
#     # InActivateCourseView,
#     # CreateNewVersionCourseView
# )
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
    # path('display/registered-course/', RegisteredCourseListView.as_view(), name='register-course-list'),
    # path('display/users/', UserListForEnrollment.as_view(), name='users-list'),
    # path('create/course-enrollments/', CreateCourseEnrollmentView.as_view(), name='create-course-enrollments-record'),
    # path('display/course-enrollments/', DisplayCourseEnrollmentView.as_view(), name='course-enrollments-list'),
    # path('enrollments/unassign/', UnAssignCourseEnrollmentView.as_view(), name='unassign-course-enrollment'),
    # path('enrollments/assign/', AssignCourseEnrollmentView.as_view(), name='assign-course-enrollment'),
    
    #createcourseview.py views url
    # # path('create/course/v1/', CreateCourseView.as_view(), name='create-course-v1'), #*
    # path('create/course/<int:course_id>/reading-material/', CreateReadingMaterialView.as_view(), name='create-course-reading-material'),
    # path('create/course/<int:course_id>/video/', CreateVideoView.as_view(), name='create-course-video'),
    # path('create/course/<int:course_id>/quiz/', CreateQuizView.as_view(), name='create-course-quiz'),
    # path('create/course/<int:course_id>/course-structure/', CreateCourseStructureForCourseView.as_view(), name='create-course-structure'),
    # path('create/<int:course_id>/quiz/<int:quiz_id>/question/', CreateQuestionView.as_view(), name='create-quiz-question'),
    # path('create/question/<int:question_id>/choices/', CreateChoiceView.as_view(), name='create-question-choice'),
    # path('active/course/<int:course_id>/', ActivateCourseView.as_view(), name='activate-course'),
    # path('inactive/course/<int:course_id>/', InActivateCourseView.as_view(), name='inactivate-course'),
    # path('create/course/<int:course_id>/versions/', CreateNewVersionCourseView.as_view(), name='create-course-v1'),

    
    #editcourseviews.py views url
    # path('course/<int:course_id>/edit/', EditCourseInstanceDetailsView.as_view(), name='edit_course_instance'),
    
    # #userdashboardviews.py views url
    # path('dashboard/sa/registration/count/', ActiveRegisteredCustomerCountView.as_view(), name='active-registration-count'),
    # path('dashboard/sa/active_registration-per-course/count/', CountOfActiveRegistrationPerCoure.as_view(), name='active_registration-per-course-count'),
    # path('dashboard/sa/progress-per-course/count/', GraphOfProgressPerCourseView.as_view(), name='not_started-per-course-count'),
    # path('dashboard/sa/course/count/', CourseCountView.as_view(), name='course-count'),
    
    
    #courseview.py  views url
    # path('courses/', AllCourseListDisplayView.as_view(), name='courses-list'),
    # path('courses/active/', ActiveCourseListDisplayView.as_view(), name='active-courses-list'),
    # path('courses/inactive/', InActiveCourseListDisplayView.as_view(), name='inactive-courses-list'),
    # path('courses/registered/', RegisterCoursesOnCostumerListDisplayView.as_view(), name='registered-courses-list'),
    # path('courses/unregistered/', UnRegisteredCoursesOnCostumerListDisplayView.as_view(), name='un-registered-courses-list'),
    # path('courses/enrolled/', EnrolledCoursesListDisplayView.as_view(), name='enrolled-courses-list'),
    # path('course/<int:course_id>/', CourseInstanceDetailDisplayView.as_view(), name='course'), #*
    # # path('course-structure/<int:course_id>/', SingleCourseStructureListDisplayView.as_view(), name='course-structure'),
    # path('course/<int:course_id>/reading/<int:content_id>/', ReadingMaterialInstanceDisplayView.as_view(), name='course-reading-material-instance'),
    # path('course/<int:course_id>/video/<int:content_id>/', VideoInstanceDisplayView.as_view(), name='course-video-instance'),
    # path('course/<int:course_id>/quiz/<int:content_id>/', QuizInstanceDisplayView.as_view(), name='course-quiz-instance'),
    # path('course/<int:course_id>/readings/', ReadingMaterialListPerCourseView.as_view(), name='course-reading-material-list'),
    # path('course/<int:course_id>/videos/', VideoMaterialListPerCourseView.as_view(), name='course-video-list'),
    # path('course/<int:course_id>/quizzes/', QuizListPerCourseView.as_view(), name='course-quiz-list'),
    # path('course/<int:course_id>/quiz/<int:quiz_id>/questions/', QuestionListPerQuizView.as_view(), name='quiz-question-list'),
    # path('course/<int:course_id>/notifications/', NotificationBasedOnCourseDisplayView.as_view(), name='course_notifications'),
    
    #registercourseviews.py views url
    # path('display/course-register-record/', DisplayCourseRegisterRecordView.as_view(), name='course-register-record-list'),
    # # path('delete/course-register-record/', DeleteCourseRegisterRecordView.as_view(), name='delete-course-register-record-list'),
    # path('delete/course/<int:pk>/register-record/', DeleteSingleCourseRegisterRecordInstanceView.as_view(), name='delete-single-course-register-record'),
    # path('deactivate/register-records/', DeactivateCourseRegistrationRecordView.as_view(), name='deactivate-register-records'), # patch with request req_mode provided , either active or inactivate
    # path('activate/register-records/', ActivateCourseRegistrationRecordView.as_view(), name='activate-register-records'), # patch with request req_mode provided , either active or inactivate
    # path('display/active/course-register-record/', DisplayActiveCourseRegisterRecordView.as_view(), name='active-course-register-record-list'), # get with filter display_status = active, inactive , else all
    # path('display/inactive/course-register-record/', DisplayInActiveCourseRegisterRecordView.as_view(), name='inactive-course-register-record-list'), # get with filter display_status = active, inactive , else all

]
