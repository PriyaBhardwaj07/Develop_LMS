from datetime import timezone
import json
from django.forms import ValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from exam.models.coremodels import User
from custom_authentication.custom_mixins import ClientAdminMixin, ClientMixin
from exam.models.allmodels import (
    Course,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory
)
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    FormView,
    CreateView,
    FormView,
    UpdateView,
)

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator

from  exam.serializers.enrollcourseserializers import (
    AssignCourseEnrollmentSerializer, 
    CourseEnrollmentSerializer,
    DisplayCourseEnrollmentSerializer,
    EnrolledCoursesSerializer,
    EnrollmentDeleteSerializer, 
    RegisteredCourseSerializer, 
    UnAssignCourseEnrollmentSerializer, 
    UserSerializer
)
from exam.models import *

# for enrollment feature
# will be displayed to employer/client-admin only

class RegisteredCourseListView(APIView,ClientAdminMixin):
    """
        view to display courses that are registered for that customer, whose's id is owned by user in request.
        trigger with GET request
        should be allowed for only [client-admin ].
    """
    def get(self, request, format=None):
        try:
            # Extract customer ID from the request body
            customer_id = request.data.get("customer_id")
            if not customer_id:
                return Response({"error": "Customer ID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            # Filter CourseRegisterRecord with customer ID and active status
            course_register_records = CourseRegisterRecord.objects.filter(customer=customer_id, active=True)

            # Check if courses exist
            if not course_register_records:
                return Response({"message": "No customer-course register record found.", "data": []}, status=status.HTTP_404_NOT_FOUND)

            # Get the list of course IDs
            course_ids = [record.course.id for record in course_register_records]
            if not course_ids:
                return Response({"error": "No courses found for the given customer ID."}, status=status.HTTP_404_NOT_FOUND)

            # Get instances of Course whose IDs are in the list
            courses = Course.objects.filter(id__in=course_ids)

            # Serialize the courses data
            serializer = RegisteredCourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, ValidationError):
                return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class UserListForEnrollmentView(APIView, ClientAdminMixin):
    """
    
    view to display data about list of user which have customer id same as that of user in request.
    trigger with GET request
    should be allowed for only [Client Admin].            
    """

    def get(self, request, format=None):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
            # Extract customer ID from the request body
            customer_id = request.data.get("customer_id")
            if not customer_id:
                return Response({"error": "Customer ID is missing in the request body."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter users based on the provided customer ID
            users = User.objects.filter(customer__id=customer_id)
            if not users:
                return Response({"error": "No users found for the given customer ID."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the user data
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateCourseEnrollmentView(APIView, ClientAdminMixin):
 
    """
        view to create instances in CourseEnrollment.
        trigger with POST request
        should be allowed for only [Client Admin].
    
    """
    
    def post(self, request, *args, **kwargs):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            # Validate request data using the serializer
            serializer = CourseEnrollmentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Extract validated course_ids and user_ids from serializer data
            course_ids = serializer.validated_data.get("course_ids")
            user_ids = serializer.validated_data.get("user_ids")

            # Lists to hold created enrollments, existing records, and all records
            enrollments = []
            existing_records = []

            # Retrieve all existing records from the database
            all_existing_records = CourseEnrollment.objects.all()

            # Iterate through course_ids and user_ids to create enrollments
            for course_id in course_ids:
                for user_id in user_ids:
                    # Check if enrollment already exists
                    record = CourseEnrollment.objects.filter(course_id=course_id, user_id=user_id).first()
                    if record:
                        # Update active status if False
                        if not record.active:
                            record.active = True
                            record_data = {
                                "id": record.id,
                                "course": record.course.id,
                                "active": record.active
                            }
                            existing_records.append(record_data)
                        else:
                            record_data = {
                                "id": record.id,
                                "course": record.course.id,
                                "active": record.active
                            }
                            existing_records.append(record_data)
                        continue  # Move to the next iteration

                    # Create a new enrollment
                    enrollment = CourseEnrollment.objects.create(course_id=course_id, user_id=user_id, active=True)
                    enrollments.append(enrollment)

            # Combine new enrollments and existing records into a single list
            all_records = list(all_existing_records.values()) + enrollments + existing_records

            # Response body including all three lists
            response_data = {
                "message": "Course enrollments have been created successfully.",
                "enrollments": enrollments,
                "existing_records": existing_records,
                "all_records": all_records
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DisplayCourseEnrollmentView(APIView, ClientAdminMixin):
    """
    View to display all instances of CourseEnrollment Table.
    Triggered with a GET request.
    Only accessible to client admin users.
    """

    def get(self, request, format=None):
        try:
            # Extract user data from the request body
            user_data = request.data.get("user")
            if not user_data:
                return Response({"error": "User data not found in the request body."}, status=status.HTTP_400_BAD_REQUEST)

            # Extract the role from the user data
            role = user_data.get("role")

            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            # Get all instances of CourseEnrollment
            enrollments = CourseEnrollment.objects.all()

            # Filter enrollments based on the role if provided
            if role is not None:
                enrollments = enrollments.filter(user__role=role)

            # Check if there are any enrollments
            if not enrollments.exists():
                return Response({"message": "No course enrollments found."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the course enrollment data
            serializer = DisplayCourseEnrollmentSerializer(enrollments, many=True)
            
            return Response(serializer.data)
        except (CourseEnrollment.DoesNotExist, DatabaseError, ValidationError) as error:
            error_message = "An error occurred: " + str(error)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnAssignCourseEnrollmentView(APIView, ClientAdminMixin):
    """
    this API is used to unassign course to specified user(s) by turning the active false , and hide visibility of course to user(s).
    required inputs : list of ids of instance of course enrollment table
    
    Method: POST
    Parameters:
        - enrollment_ids (list of integers): IDs of course enrollment instances to unassign.
    
    It is triggered with POST request.
    
    """
    def post(self, request, *args, **kwargs):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            # Deserialize and validate the input data
            serializer = UnAssignCourseEnrollmentSerializer(data=request.data)
            if serializer.is_valid():
                enrollment_ids = serializer.validated_data.get('enrollment_ids')

                # Check if any enrollment IDs were provided
                if not enrollment_ids:
                    return Response({'error': 'No enrollment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if any provided enrollment IDs are not found in the database
                enrollments = CourseEnrollment.objects.filter(id__in=enrollment_ids)
                if len(enrollments) != len(enrollment_ids):
                    return Response({'error': 'One or more enrollment IDs do not exist'}, status=status.HTTP_404_NOT_FOUND)

                # Iterate through each enrollment and update its active status
                updated_enrollments = []
                for enrollment in enrollments:
                    if enrollment.active:
                        enrollment.active = False
                        enrollment.save()
                        updated_enrollments.append(enrollment.id)
                    else:
                        updated_enrollments.append({'id': enrollment.id, 'message': 'Enrollment is already inactive'})

                return Response({'message': f'Courses unassigned successfully.', 'updated_enrollments': updated_enrollments}, status=status.HTTP_200_OK)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class AssignCourseEnrollmentView(APIView, ClientAdminMixin):
    """
    this API is used to assign course to specified user(s) for all users in courseenrollment table who have active false
    in request body : list of ids of instance of course enrollment table
    
    
    """
    def post(self, request, *args, **kwargs):
        # Check if the user has client admin privileges
        if not self.has_client_admin_privileges(request):
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignCourseEnrollmentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            enrollment_ids = serializer.validated_data.get('enrollment_ids', [])

            if not enrollment_ids:
                return Response({'error': 'No enrollment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate that all provided IDs are integers
            if not all(isinstance(enrollment_id, int) for enrollment_id in enrollment_ids):
                return Response({'error': 'All enrollment IDs must be integers'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if enrollments exist and are inactive
            enrollments_to_update = CourseEnrollment.objects.filter(id__in=enrollment_ids, active=False)

            if not enrollments_to_update.exists():
                # Check if any provided enrollment IDs are already active
                active_enrollments = CourseEnrollment.objects.filter(id__in=enrollment_ids, active=True)
                if active_enrollments.exists():
                    active_ids = [enrollment.id for enrollment in active_enrollments]
                    return Response({'warning': 'One or more enrollments are already active',
                                     'active_enrollment_ids': active_ids}, status=status.HTTP_409_CONFLICT)

                return Response({'error': 'No valid enrollments found to update'}, status=status.HTTP_404_NOT_FOUND)

            # Perform the update operation inside a transaction
            with transaction.atomic():
                updated_count = enrollments_to_update.update(active=True)

            return Response({'message': 'Course(s) assigned successfully', 'updated_count': updated_count},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EnrolledCoursesListDisplayView(APIView, ClientMixin):
    """  
    trigger with GET request
    should be allowed for only [Client].
    GET Request 
    this view is so that the client can see their enrolled courses
    """
    def get(self, request, format=None):
        try:
            # Retrieve user ID from request headers
            user_id = request.headers.get("user")
            if user_id is None:
                return Response({"error": "User ID not found in headers."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve enrolled courses for the user that are active
            enrolled_courses = CourseEnrollment.objects.filter(user_id=user_id, course__active=True)
            
            # Serialize the enrolled courses data
            serializer = EnrolledCoursesSerializer(enrolled_courses, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

