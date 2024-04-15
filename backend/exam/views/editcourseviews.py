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
from exam.serializers.editcourseserializers import EditCourseInstanceSerializer, EditQuestionInstanceSerializer, EditQuizInstanceSerializer, EditVideoMaterialSerializer, EditingQuestionInstanceOnConfirmationSerializer, EditingQuizInstanceOnConfirmationSerializer, NotificationSerializer
from exam.models.allmodels import (
    ActivityLog,
    Course,
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

class EditCourseInstanceDetailsView(APIView):

    def post(self, request, format=None):
        try:
            course_id = request.data.get('course_id')
            course = Course.objects.get(pk=course_id)
            if not course:
                raise Course.DoesNotExist("No course found with the provided course ID.")
            if course.deleted_at:
                raise ValidationError("Course instance has been deleted")
            
            serializer = EditCourseInstanceSerializer(data=request.data)
            if serializer.is_valid():
                course.title = serializer.validated_data.get('title')
                course.summary = serializer.validated_data.get('summary')
                course.updated_at = timezone.now()
                course.save()

                if course.active:
                    latest_activity_log = ActivityLog.objects.latest('created_at')
                    notification = Notification.objects.create(
                        message=latest_activity_log.message,
                        course=course
                    )
                    notification_data = {
                        "message": notification.message,
                        "created_at": notification.created_at
                    }
                    return Response({"message": "Course instance updated successfully", "notification": notification_data}, status=status.HTTP_200_OK)
                return Response({"message": "Course instance updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except (ValidationError, Course.DoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationBasedOnCourseDisplayView(APIView):
    
    # TODO : THE FUNCTIONALITY TO ENABLE THE VIEW OF NOTIFICATIONS, IF NOTIFICATION FOR THAT COURSES ARE NEWER THE ENROLLMENT DATE OF COURSE ENROLLMENT, THEN REFLECT IN NOTIFICATION FOLDER OF USER
    def get(self, request, course_id, format=None):
        try:
            # Get the course enrollment date for the current user
            course_enrollment = CourseEnrollment.objects.get(user=request.user, course_id=course_id)
            enrollment_date = course_enrollment.created_at

            # Get notifications for the specified course
            notifications = Notification.objects.filter(course_id=course_id)

            # Check if there are any notifications for the given course
            if notifications.exists():
                # Filter notifications based on creation date
                new_notifications = notifications.filter(created_at__gt=enrollment_date)
                if new_notifications.exists():
                    serializer = NotificationSerializer(new_notifications, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "No new notifications for this course yet."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No notifications for this course yet."}, status=status.HTTP_200_OK)
        
        except (CourseEnrollment.DoesNotExist, Notification.DoesNotExist) as e:
            if isinstance(e, CourseEnrollment.DoesNotExist):
                return Response({"error": "User is not enrolled in this course."}, status=status.HTTP_404_NOT_FOUND)
            elif isinstance(e, Notification.DoesNotExist):
                return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# TODO CHECK 
class EditingQuizInstanceOnConfirmation(APIView):
    def post(self, request, course_id, quiz_id, format=None):
        try:
            serializer = EditingQuizInstanceOnConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            confirmation = serializer.validated_data['confirmation']
            quiz = Quiz.objects.get(pk=quiz_id)
            course = quiz.courses.first()  # Assuming each quiz is related to only one course
            
            if confirmation:
                # Editing existing quiz instance
                if course.active:
                    return Response({"error": "Editing is not allowed for active courses."},
                                    status=status.HTTP_403_FORBIDDEN)

                quiz.title = serializer.validated_data.get('title', quiz.title)
                quiz.description = serializer.validated_data.get('description', quiz.description)
                quiz.answers_at_end = serializer.validated_data.get('answers_at_end', quiz.answers_at_end)
                quiz.exam_paper = serializer.validated_data.get('exam_paper', quiz.exam_paper)
                quiz.pass_mark = serializer.validated_data.get('pass_mark', quiz.pass_mark)
                quiz.updated_at = timezone.now()
                quiz.save()

                return Response({"message": "Quiz instance updated successfully."}, status=status.HTTP_200_OK)
            else:
                # Creating new quiz instance
                new_quiz = Quiz.objects.create(
                    title=serializer.validated_data.get('title'),
                    description=serializer.validated_data.get('description'),
                    answers_at_end=serializer.validated_data.get('answers_at_end'),
                    exam_paper=serializer.validated_data.get('exam_paper'),
                    pass_mark=serializer.validated_data.get('pass_mark'),
                )

                # Update CourseStructure entry with the new quiz id
                CourseStructure.objects.filter(course=course_id, content_type='quiz', content_id=quiz_id) \
                    .update(content_id=new_quiz.id)

                return Response({"message": "New quiz instance created successfully."}, status=status.HTTP_201_CREATED)
        
        except (Quiz.DoesNotExist, Exception) as e:
            if isinstance(e, Quiz.DoesNotExist):
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        
class EditingQuestionInstanceOnConfirmation(APIView):
    def post(self, request, course_id, quiz_id, format=None):
        try:
            serializer = EditingQuestionInstanceOnConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            confirmation = serializer.validated_data['confirmation']
            quiz = Quiz.objects.get(pk=quiz_id)
            questions = quiz.questions.all()
            
            if confirmation:
                # Editing existing question instances
                for question in questions:
                    question.figure = serializer.validated_data.get('figure', question.figure)
                    if 'content' in serializer.validated_data and serializer.validated_data['content'] is not None:
                        question.content = serializer.validated_data['content']
                    question.explanation = serializer.validated_data.get('explanation', question.explanation)
                    question.choice_order = serializer.validated_data.get('choice_order', question.choice_order)
                    question.updated_at = timezone.now()
                    question.save()
                
                return Response({"message": "Question instances updated successfully."}, status=status.HTTP_200_OK)
            else:
                # Do not allow updating, suggest creating a new question
                return Response({"message": "You chose not to update existing questions. Please create new ones instead."},
                                status=status.HTTP_400_BAD_REQUEST)
        
        except (Quiz.DoesNotExist, Exception) as e:
            if isinstance(e, Quiz.DoesNotExist):
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ====================================================
# AFTER VIDEO CONFIGURATION
# ================================================            
class EditVideoMaterialInstanceView(APIView):
    pass