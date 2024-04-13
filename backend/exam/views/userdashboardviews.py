from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from custom_authentication.custom_mixins import SuperAdminMixin
from exam.serializers.dashboardserializers import ActiveCourseCountSerializer, ActiveRegistrationCountSerializer, InActiveCourseCountSerializer
from exam.serializers.editcourseserializers import EditCourseInstanceSerializer, NotificationSerializer
from exam.models.allmodels import (
    ActivityLog,
    Course,
    CourseCompletionStatusPerUser,
    Notification,
    UploadVideo,
    UploadReadingMaterial,
    CourseStructure,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory
)
from rest_framework.exceptions import NotFound, ValidationError

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
# from exam.models.coremodels import *
from exam.serializers.createcourseserializers import (
    ActivateCourseSerializer,
    CourseSerializer, 
    CourseStructureSerializer,
    CreateChoiceSerializer,
    InActivateCourseSerializer, 
    UploadReadingMaterialSerializer, 
    UploadVideoSerializer, 
    QuizSerializer, 
    CreateCourseSerializer,
    CreateUploadReadingMaterialSerializer,
    CreateUploadVideoSerializer,
    CreateQuizSerializer,
    CreateQuestionSerializer,
)
import pandas as pd # type: ignore

# =================================================================
# employee dashboard
# =================================================================

class CreateCourseCompletionStatusPerUserView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            completion_status = (default=False)
            in_progress_status = (default=False)
            created_at = (auto_now_add=True)
    """
    pass

class CreateQuizScoreView(APIView):
    """
        allowed for client admin
        POST request
        triggered after course enrollment records creation , similar to that one.
                in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
                        each course in list will be mapped for all users in list
        while creating instance :
            enrolled_user = request body
            course = request body
            total_quizzes_per_course = calculate in view for course by counting active quizzes in it
            completed_quiz_count = by default 0
            total_score_per_course = (default=0)
    """
    pass

class UpdateCompleteQuizCountView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true , if set of quiz, course, user doesn't already have completed = true in table
        while updating instance :
            completed_quiz_count = increment by 1
    """
    pass

class UpdateTotalScorePerCourseView(APIView):
    """
        POST request
        triggered when quiz attempt history for that course, that user have completed =true 
        while updating instance :
            total_score_per_course -> calculate for it 
    """
    pass

class UpdateCourseCompletionStatusPerUserView(APIView):
    """
        POST request
        triggers when 
        total_quizzes_per_course = completed_quiz_count in quiz score for that user in request
        if total_quizzes_per_course == completed_quiz_count:
            completion_status=True and in_progress_status =False
        if total_quizzes_per_course > completed_quiz_count:
            completion_status=False and in_progress_status =True
    """
    pass

class DisplayClientCourseProgressView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table
        
        display if user in request have active enrollment for the course
        display:
            completed_quiz_count
    """
    pass

class DisplayClientCourseCompletionStatusView(APIView):
    """
        GET request
        for user in request, if he have data in course enrollment table(active)
        display:
            completion_status or in_progress_status = Based on which is true for the user for thi course
    """
    pass

class CountOfAssignedCoursesView(APIView):
    """
    GET request
    for user in request , count the number of active enrollments he have in course enrollment table
    """
    pass

class CountClientCompletedCourseView(APIView):
    """
        GET request
        for the user filter the CourseCompletionStatusPerUser table
        and count courses for which completion_status= True and in_progress_status = False as completed courses
        and count courses for which completion_status= False and in_progress_status = True as completed courses
    """
    pass

# =================================================================
# employer dashboard
# =================================================================

class ActiveEnrolledUserCountPerCustomerView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

class RegisteredCourseCountView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

#---------
# graph : (per course)(for a customer) [employeer (client admin) dashboard]
class CountOfCompletionPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfInProgressPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfNotStartedPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass
#---------

# =================================================================
# super admin dashboard
# =================================================================
class ActiveRegisteredCustomerCountView(SuperAdminMixin,APIView):
    """get api
    for super admin
    """
    def get(self, request):
        try:
            if not self.has_super_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            active_registration_count = CourseRegisterRecord.objects.filter(active=True, deleted_at__isnull=True).values('customer').distinct().count()
            print(active_registration_count)
            if active_registration_count == 0:
                return Response({"message": "no active registration were found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ActiveRegistrationCountSerializer({'active_registered_customer_count': active_registration_count})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, ValidationError):
                return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# graph to count registrations per course 
class CountOfActiveRegistrationPerCoure(SuperAdminMixin,APIView):
    """
        get request
        
        for super admin
        
        get list of active courses from course table
        and for each course count instances from course registration records which are active =true, deleted_at =null
        and pass this data in response for each course send it's calculated count
    """

    def get(self, request):
        try:
            if not self.has_super_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            active_courses = Course.objects.filter(active=True, deleted_at__isnull=True)
            if not active_courses:
                return Response({"message": "no active course found"},status=status.HTTP_404_NOT_FOUND)

            course_active_registration_counts = []
            for course in active_courses:
                active_registration_count = CourseRegisterRecord.objects.filter(
                    course=course,
                    active=True,
                    deleted_at__isnull=True
                ).count()
                if not active_registration_count.exists():
                    return Response({"error": "Course Registration not found"}, status=status.HTTP_404_NOT_FOUND)
                course_active_registration_counts.append({
                    'course_id': course.id,
                    'course_title': course.title,
                    'active_registration_count': active_registration_count
                })
            return Response(course_active_registration_counts, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GraphOfProgressPerCourseView(SuperAdminMixin,APIView):

    def get(self, request):
        try:
            if not self.has_super_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            active_courses = Course.objects.filter(active=True, deleted_at__isnull=True)
            if not active_courses:
                return Response({"message": "no active course found"},status=status.HTTP_404_NOT_FOUND)

            course_progress_counts = []
            for course in active_courses:
                completion_count = CourseCompletionStatusPerUser.objects.filter(
                    course=course,
                    active=True,
                    completion_status=True,
                    in_progress_status=False
                ).count()
                in_progress_count = CourseCompletionStatusPerUser.objects.filter(
                    course=course,
                    active=True,
                    # completion_status=False,
                    in_progress_status=True
                ).count()
                not_started_count = CourseCompletionStatusPerUser.objects.filter(
                    course=course,
                    active=True,
                    completion_status=False,
                    in_progress_status=True
                ).count()
                course_progress_counts.append({
                    'course_id': course.id,
                    'course_title': course.title,
                    'completion_count': completion_count,
                    'course_in_progress_count': in_progress_count,
                    'course_not_started_count': not_started_count
                })
            return Response(course_progress_counts, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, (CourseCompletionStatusPerUser.DoesNotExist)):
                return Response({"error": "Course Completion Status not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseCountView(SuperAdminMixin, APIView):
    """
    GET API for super admin to get count of active and inactive courses separately.
    """

    def get(self, request):
        try:
            if not self.has_super_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            active_course_count = Course.objects.filter(active=True, deleted_at__isnull=True).count()
            inactive_course_count = Course.objects.filter(active=False, deleted_at__isnull=True).count()
            if active_course_count == 0:
                active_response = {"message": "No active courses were found"}
            else:
                active_serializer = ActiveCourseCountSerializer({'active_course_count': active_course_count})
                active_response = active_serializer.data
            if inactive_course_count == 0:
                inactive_response = {"message": "No inactive courses were found"}
            else:
                inactive_serializer = InActiveCourseCountSerializer({'inactive_course_count': inactive_course_count})
                inactive_response = inactive_serializer.data
            return Response({
                "active_courses": active_response,
                "inactive_courses": inactive_response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, (ValidationError, Course.DoesNotExist)):
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
