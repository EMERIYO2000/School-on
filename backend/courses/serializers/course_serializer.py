# courses/serializers.py
from rest_framework import serializers
from ..models import (
    Category, StateExam, ExamQuestion, ExamChoice, ArchiveResource, Course, Chapter, ContentBlock, LearnerQuestion, Lesson,
    Quiz, Question, Choice, Enrollment, 
    LessonProgress, QuizAttempt, AttemptAnswer, CourseReview
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class ExamChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamChoice
        fields = ['id', 'text', 'is_correct']


class ExamQuestionSerializer(serializers.ModelSerializer):
    choices = ExamChoiceSerializer(many=True, required=False)

    class Meta:
        model = ExamQuestion
        fields = ['id', 'text', 'explanation', 'order', 'choices']


class StateExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(many=True, read_only=True)
    resources = serializers.SerializerMethodField()

    class Meta:
        model = StateExam
        fields = ['id', 'title', 'year', 'subject', 'session', 'creator', 'status', 'review_note', 'questions', 'resources', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'status', 'review_note', 'created_at', 'updated_at']

    def get_resources(self, obj):
        return ArchiveResourceSerializer(obj.resources.all(), many=True, context=self.context).data


class ArchiveResourceSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ArchiveResource
        fields = ['id', 'exam', 'title', 'resource_type', 'file', 'download_url', 'description', 'downloadable', 'created_at']
        read_only_fields = ['id', 'download_url', 'created_at']

    def get_download_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if request and obj.file else (obj.file.url if obj.file else None)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'order', 'choices', 'explanation']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'quiz_type', 'subject', 'school_level',
            'year', 'session', 'series', 'duration', 'shuffle_questions',
            'shuffle_choices', 'is_final_assessment', 'status', 'xp_reward', 'questions',
        ]


class QuizChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']


class QuizQuestionCreateSerializer(serializers.ModelSerializer):
    choices = QuizChoiceCreateSerializer(many=True, required=False, default=list)

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points', 'order', 'correct_numeric', 'explanation', 'choices']

    def validate_choices(self, choices):
        if not choices:
            raise serializers.ValidationError('Une question doit avoir au moins une réponse.')
        return choices

    def validate(self, attrs):
        question_type = attrs.get('question_type', 'SINGLE_CHOICE')
        choices = attrs.get('choices', [])
        correct_count = sum(choice['is_correct'] for choice in choices)
        if question_type in {'SINGLE_CHOICE', 'TRUE_FALSE'} and correct_count != 1:
            raise serializers.ValidationError('Cette question doit avoir exactement une bonne réponse.')
        if question_type in {'SINGLE_CHOICE', 'TRUE_FALSE', 'MULTIPLE_CHOICE'} and len(choices) < 2:
            raise serializers.ValidationError('Cette question doit avoir au moins deux choix.')
        if question_type == 'MULTIPLE_CHOICE' and correct_count < 1:
            raise serializers.ValidationError('Un choix multiple doit avoir au moins une bonne réponse.')
        if question_type == 'NUMERIC' and attrs.get('correct_numeric') is None:
            raise serializers.ValidationError({'correct_numeric': 'La réponse numérique est obligatoire.'})
        if question_type == 'TRUE_FALSE' and len(choices) != 2:
            raise serializers.ValidationError('Une question Vrai/Faux doit avoir deux réponses.')
        return attrs


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuizQuestionCreateSerializer(many=True, min_length=1)

    class Meta:
        model = Quiz
        fields = [
            'id', 'course', 'chapter', 'title', 'description', 'quiz_type',
            'subject', 'school_level', 'year', 'session', 'series', 'duration',
            'shuffle_questions', 'shuffle_choices', 'is_final_assessment', 'xp_reward', 'questions',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        chapter = attrs.get('chapter')
        course = attrs['course']
        if chapter and chapter.course_id != course.id:
            raise serializers.ValidationError({'chapter': 'Ce chapitre n’appartient pas au cours indiqué.'})
        return attrs

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(quiz=quiz, created_by=self.context['request'].user, **question_data)
            Choice.objects.bulk_create(
                [Choice(question=question, **choice_data) for choice_data in choices_data]
            )
        return quiz


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'chapter', 'title', 'content_type', 
            'text_content', 'file', 'video_url', 
            'order', 'is_free_preview', 'is_completed'
        ]

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonProgress.objects.filter(
                student=request.user, lesson=obj, is_completed=True
            ).exists()
        return False


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    content_blocks = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'summary', 'description', 'order', 'lessons', 'content_blocks']

    def get_content_blocks(self, obj):
        return ContentBlockSerializer(obj.content_blocks.all(), many=True, context=self.context).data


class ContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlock
        fields = ['id', 'chapter', 'content_type', 'title', 'text_content', 'file', 'url', 'language', 'caption', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LearnerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerQuestion
        fields = ['id', 'learner', 'course', 'chapter', 'content_block', 'question', 'answer', 'status', 'created_at', 'answered_at']
        read_only_fields = ['id', 'learner', 'course', 'status', 'answer', 'created_at', 'answered_at']


class LearnerQuestionAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField()


class CourseListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    teacher_name = serializers.ReadOnlyField(source='teacher.get_full_name')

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 'description',
            'teacher', 'teacher_name', 'level', 'thumbnail', 'summary',
            'price', 'is_premium', 'is_state_exam_prep', 'certification_enabled', 'minimum_progress',
            'minimum_quiz_score', 'all_quizzes_required', 'require_final_assessment', 'require_final_project',
            'require_mentor_approval', 'status', 'review_note', 'reviewed_at', 'created_at'
        ]
        read_only_fields = ['id', 'teacher', 'status', 'review_note', 'reviewed_at', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    teacher_name = serializers.ReadOnlyField(source='teacher.get_full_name')
    chapters = ChapterSerializer(many=True, read_only=True)
    unassigned_lessons = serializers.SerializerMethodField()
    quizzes = QuizSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'summary', 'description', 'learning_objectives', 'category',
            'teacher_name', 'level', 'thumbnail', 'price', 
            'estimated_duration', 'status', 'review_note', 'reviewed_at', 'is_premium', 'is_state_exam_prep', 'chapters',
            'unassigned_lessons', 'quizzes', 'is_enrolled', 'certification_enabled', 'minimum_progress',
            'minimum_quiz_score', 'all_quizzes_required', 'require_final_assessment', 'require_final_project', 'require_mentor_approval'
        ]

    def get_unassigned_lessons(self, obj):
        lessons = obj.lessons.filter(chapter__isnull=True)
        return LessonSerializer(lessons, many=True, context=self.context).data

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user, course=obj, status='active'
            ).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'status', 'enrolled_at']
        read_only_fields = ['id', 'student', 'enrolled_at']


class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.get_full_name')

    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'student', 'student_name', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'course', 'student', 'student_name', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('La note doit être comprise entre 1 et 5.')
        return value


class QuizSubmitSerializer(serializers.Serializer):
    """Permet de soumettre les réponses d'un quiz et de calculer le score."""
    answers = serializers.JSONField(
        help_text="Format accepté: {'1': 4} ou [{'question_id': 1, 'choice_id': 4}]"
    )

    def validate_answers(self, value):
        if isinstance(value, dict):
            normalized = {}
            for question_id, choice_id in value.items():
                if isinstance(choice_id, list):
                    try:
                        normalized[str(question_id)] = [int(item) for item in choice_id]
                    except (TypeError, ValueError):
                        raise serializers.ValidationError('Les identifiants de choix doivent être numériques.')
                else:
                    try:
                        normalized[str(question_id)] = int(choice_id)
                    except (TypeError, ValueError):
                        normalized[str(question_id)] = str(choice_id)
            return normalized

        if isinstance(value, list):
            normalized = {}
            for item in value:
                if not isinstance(item, dict):
                    raise serializers.ValidationError('Chaque réponse doit être un objet avec question_id et choice_id.')

                question_id = item.get('question_id')
                choice_id = item.get('choice_id', item.get('choice_ids'))
                if question_id is None or choice_id is None:
                    raise serializers.ValidationError('Chaque réponse doit contenir question_id et choice_id.')

                if isinstance(choice_id, list):
                    normalized[str(question_id)] = [int(item) for item in choice_id]
                else:
                    try:
                        normalized[str(question_id)] = int(choice_id)
                    except (TypeError, ValueError):
                        normalized[str(question_id)] = str(choice_id)
            return normalized

        raise serializers.ValidationError('Le champ answers doit être un dictionnaire ou une liste d’objets.')


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.ReadOnlyField(source='quiz.title')

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'score', 'raw_score', 'max_score', 'percentage', 'correct_answers', 'wrong_answers', 'status', 'started_at', 'submitted_at', 'completed_at']
        read_only_fields = fields

    percentage = serializers.FloatField(source='score', read_only=True)