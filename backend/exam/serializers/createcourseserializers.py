from rest_framework import serializers
from exam.models.allmodels import Choice, Course, CourseStructure, Question, UploadReadingMaterial, UploadVideo, Quiz
from django.utils import timezone

class CreateCourseSerializer(serializers.ModelSerializer):
    
    def validate(self, data):
        """
        Validate the input data.
        """
        title = data.get('title')
        summary = data.get('summary')
        # Check if title is provided and not empty
        if not title:
            raise serializers.ValidationError("Title is required.")
        # # Check if summary is provided and not empty
        # if not summary:
        #     raise serializers.ValidationError("Summary is required.")
        return data
    class Meta:
        model = Course
        fields = ['title', 'summary']
        
class CreateUploadReadingMaterialSerializer(serializers.ModelSerializer):
    
    def validate(self, data):
        """
        Validate the input data.
        """
        title = data.get('title')
        reading_content = data.get('reading_content')
        # Check if title is provided and not empty
        if not title:
            raise serializers.ValidationError("Title is required.")
        # # Check if reading_content is provided and not empty
        if not reading_content:
            raise serializers.ValidationError("reading_content is required.")
        return data
    class Meta:
        model = UploadReadingMaterial
        fields = ['title', 'reading_content']
        
class CreateUploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = ['title', 'video', 'summary']
        
class CreateQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['title', 'random_order', 'answers_at_end', 'exam_paper', 'pass_mark']
        
class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['figure', 'content', 'explanation', 'choice_order']
        
class CreateChoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for creating choices.
    """

    def __init__(self, *args, **kwargs):
        self.question_id = kwargs.pop('question_id', None)
        super().__init__(*args, **kwargs)

    def validate(self, data):
        choice = data.get('choice')
        correct = data.get('correct')

        if not choice:
            raise serializers.ValidationError("Choice cannot be empty")

        if correct not in [True, False]:
            raise serializers.ValidationError("Correct field must be either true or false")

        return data
    class Meta:
        model = Choice
        fields = ['choice', 'correct']

    def create(self, validated_data):
        question_id = self.context.get('question_id')
        question = Question.objects.get(pk=question_id)
        choice = Choice.objects.create(question=question, **validated_data)
        return choice
    
class CourseSerializer(serializers.ModelSerializer):
    
    def validate(self, data):
        if 'title' not in data:
            raise serializers.ValidationError("Title is required")
        if not data['title'].strip():
            raise serializers.ValidationError("Title cannot be empty")
        if 'summary' not in data:
            raise serializers.ValidationError("Summary is required")
        if not data['summary'].strip():
            raise serializers.ValidationError("Summary cannot be empty")
        if 'original_course' not in data:
            raise serializers.ValidationError("Original course ID is required")
        if 'version_number' not in data:
            raise serializers.ValidationError("Version number is required")
        version_number = data.get('version_number')
        if not isinstance(version_number, int) or version_number <= 0:
            raise serializers.ValidationError("Version number must be a positive integer")

        data['active'] = False
        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        return data
    class Meta:
        model = Course
        fields = '__all__'

class CourseStructureSerializer(serializers.ModelSerializer):
    
    def validate(self, data):
        # Check if course is provided
        if 'course' not in data:
            raise serializers.ValidationError("Course is required")
        # Check if order_number is provided
        if 'order_number' not in data:
            raise serializers.ValidationError("Order number is required")
        # Check if content_type is provided
        if 'content_type' not in data:
            raise serializers.ValidationError("Content type is required")
        # Check if content_id is provided
        if 'content_id' not in data:
            raise serializers.ValidationError("Content ID is required")
        order_number = data.get('order_number')
        if order_number is not None and order_number <= 0:
            raise serializers.ValidationError("Order number must be a positive integer")
        return data
    class Meta:
        model = CourseStructure
        fields = '__all__'

class UploadReadingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadReadingMaterial
        fields = '__all__'

class UploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    
    def validate(self, data):
        if 'title' in data:
            title = data['title']
            if len(title) < 5:
                raise serializers.ValidationError("Title must be at least 5 characters long.")
        if 'pass_mark' in data:
            pass_mark = data['pass_mark']
            if pass_mark < 0 or pass_mark > 100:
                raise serializers.ValidationError("Pass mark must be between 0 and 100.")
        return data
    class Meta:
        model = Quiz
        fields = '__all__'

class InActivateCourseSerializer(serializers.Serializer):
    """
    Serializer for inactivating a course.
    """
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(pk=value)
            return course
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist.")
        
class ActivateCourseSerializer(serializers.Serializer):
    """
    Serializer for activating a course.
    """
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(pk=value)
            # Check if there are any instances related to this course in CourseStructure
            if CourseStructure.objects.filter(course=course, content_type="quiz", content_id__isnull=False).exists():
                return course  # Return the course object instance
            else:
                raise serializers.ValidationError("Cannot activate course. Construct course structure first with minimum one quiz.")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")