# courses/serializers/course_serializer.py
from rest_framework import serializers
from ..models import (
    Category, StateExam, ExamQuestion, ExamChoice, ArchiveResource, Course, Chapter, ContentBlock, LearnerQuestion, Lesson,
    Quiz, Question, Choice, Enrollment, 
    LessonProgress, QuizAttempt, AttemptAnswer, CourseReview
)
from .quiz_serializer import (
    QuizSerializer,
    QuizQuestionLearnerSerializer,
    QuizQuestionStaffSerializer,
    QuizQuestionWriteSerializer,
    QuizChoiceLearnerSerializer,
    QuizChoiceStaffSerializer,
    QuizAttemptSerializer,
    QuizAttemptDetailSerializer,
    AttemptAnswerSerializer,
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


class ChoiceSerializer(QuizChoiceStaffSerializer):
    """Alias historique : un choix de réponse vu par le créateur (corrigé inclus)."""


<<<<<<< Updated upstream:backend/courses/serializers/course_serializer.py
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
=======
class QuestionSerializer(QuizQuestionStaffSerializer):
    """Alias historique : question complète pour le créateur / l'admin."""
>>>>>>> Stashed changes:courses/serializers/course_serializer.py


class QuizChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'order']


class QuizQuestionCreateSerializer(QuizQuestionWriteSerializer):
    """Création d'une question complète au moment de la création du quiz."""

    def validate_choices(self, choices):
        if not choices:
            raise serializers.ValidationError('Une question doit avoir au moins une réponse.')
        return choices


class QuizCreateSerializer(serializers.ModelSerializer):
    """Création d'un quiz complet (métadonnées + questions) — spec §13.

    Le champ ``course`` est optionnel : le Quiz Game, le Quiz Training et la
    préparation aux examens d'État sont autonomes (spec §14 / §15).
    """
    questions = QuizQuestionCreateSerializer(many=True, min_length=1, required=False)

    class Meta:
        model = Quiz
        fields = [
<<<<<<< Updated upstream:backend/courses/serializers/course_serializer.py
            'id', 'course', 'chapter', 'title', 'description', 'quiz_type',
            'subject', 'school_level', 'year', 'session', 'series', 'duration',
            'shuffle_questions', 'shuffle_choices', 'is_final_assessment', 'xp_reward', 'questions',
=======
            'id', 'course', 'chapter', 'category', 'title', 'description',
            'quiz_type', 'subject', 'level', 'school_level', 'year', 'session',
            'series', 'duration', 'shuffle_questions', 'shuffle_choices',
            'random_question_count', 'allow_multiple_attempts', 'max_attempts',
            'passing_score', 'xp_reward', 'questions',
>>>>>>> Stashed changes:courses/serializers/course_serializer.py
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        chapter = attrs.get('chapter')
        course = attrs.get('course')
        if chapter and course and chapter.course_id != course.id:
            raise serializers.ValidationError({'chapter': 'Ce chapitre n’appartient pas au cours indiqué.'})
        if chapter and not course:
            attrs['course'] = chapter.course
        if not attrs.get('questions') and not attrs.get('course'):
            raise serializers.ValidationError(
                {'questions': 'Un quiz autonome (Game / Training / Examen) doit contenir au moins une question.'}
            )
        return attrs

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        request = self.context['request']
        quiz = Quiz.objects.create(created_by=request.user, **validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(quiz=quiz, created_by=request.user, **question_data)
            Choice.objects.bulk_create([
                Choice(question=question, **{'order': choice.get('order') or index, **choice})
                for index, choice in enumerate(choices_data, start=1)
            ])
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
    """Chapitre d'un cours — lecture pour l'apprenant, écriture pour le créateur.

    Le champ ``course`` n'est visible que pour le créateur / l'admin : côté
    apprenant il n'est pas utile de découvrir l'identifiant interne du cours.
    """
    lessons = LessonSerializer(many=True, read_only=True)
    content_blocks = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    content_blocks_count = serializers.SerializerMethodField()
    course_title = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = Chapter
        fields = [
            'id', 'course', 'course_title', 'title', 'summary', 'description', 'order',
            'lessons', 'content_blocks', 'quizzes', 'content_blocks_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_content_blocks(self, obj):
        return ContentBlockSerializer(obj.content_blocks.all(), many=True, context=self.context).data

    def get_quizzes(self, obj):
        return [
            {
                'id': quiz.id,
                'title': quiz.title,
                'quiz_type': quiz.quiz_type,
                'status': quiz.status,
                'questions_count': quiz.questions_count,
                'duration': quiz.duration,
            }
            for quiz in obj.quizzes.all()
        ]

    def get_content_blocks_count(self, obj):
        return obj.content_blocks.count()


class ContentBlockSerializer(serializers.ModelSerializer):
    """Bloc de contenu dynamique d'un chapitre (spec §6)."""
    chapter_title = serializers.ReadOnlyField(source='chapter.title')
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentBlock
        fields = [
            'id', 'chapter', 'chapter_title', 'content_type', 'title', 'text_content',
            'file', 'file_url', 'url', 'language', 'caption', 'order',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def validate(self, attrs):
        """Valide les champs obligatoires selon le type de bloc (spec §6.1)."""
        instance = getattr(self, 'instance', None)
        content_type = attrs.get('content_type', getattr(instance, 'content_type', 'TEXT'))
        required = {
            'TEXT': ['text_content'],
            'IMAGE': ['file'],
            'VIDEO': [],
            'DOCUMENT': ['file'],
            'CODE': ['text_content'],
            'RESOURCE': ['url'],
        }[content_type]
        if content_type == 'VIDEO':
            file_value = attrs.get('file', getattr(instance, 'file', None))
            url_value = attrs.get('url', getattr(instance, 'url', None))
            if not file_value and not url_value:
                raise serializers.ValidationError(
                    {'file': 'Un fichier ou une URL vidéo est obligatoire.'}
                )
        for field in required:
            value = attrs.get(field, getattr(instance, field, None))
            if not value:
                other = 'url' if field == 'file' and attrs.get('url') else None
                if other:
                    continue
                raise serializers.ValidationError(
                    {field: f'Ce champ est obligatoire pour un contenu de type {content_type}.'}
                )
        return attrs


class LearnerQuestionSerializer(serializers.ModelSerializer):
    """Question d'un apprenant sur un chapitre (spec §8)."""
    learner_name = serializers.SerializerMethodField()
    chapter_title = serializers.ReadOnlyField(source='chapter.title')
    course_title = serializers.ReadOnlyField(source='course.title')
    answered_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LearnerQuestion
        fields = [
            'id', 'learner', 'learner_name', 'course', 'course_title', 'chapter',
            'chapter_title', 'content_block', 'question', 'answer', 'status',
            'answered_by', 'answered_by_name', 'created_at', 'answered_at',
        ]
        read_only_fields = [
            'id', 'learner', 'learner_name', 'status', 'answer', 'answered_by',
            'answered_by_name', 'created_at', 'answered_at',
        ]

    def get_learner_name(self, obj):
        user = obj.learner
        return user.get_full_name() or user.username

    def get_answered_by_name(self, obj):
        if not obj.answered_by:
            return None
        return obj.answered_by.get_full_name() or obj.answered_by.username

    def validate(self, attrs):
        course = attrs.get('course')
        chapter = attrs.get('chapter')
        content_block = attrs.get('content_block')
        if chapter and course and chapter.course_id != course.id:
            raise serializers.ValidationError({'chapter': 'Ce chapitre n’appartient pas au cours indiqué.'})
        if content_block and chapter and content_block.chapter_id != chapter.id:
            raise serializers.ValidationError(
                {'content_block': 'Ce contenu n’appartient pas au chapitre indiqué.'}
            )
        if attrs.get('question') is not None and len(str(attrs['question']).strip()) < 5:
            raise serializers.ValidationError({'question': 'La question doit contenir au moins 5 caractères.'})
        return attrs


class LearnerQuestionAnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(min_length=2)



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
    """Soumission des réponses d'un quiz.

    Formats acceptés (rétrocompatibles) :
        {"answers": {"1": 4, "2": [7, 9], "3": "60", "4": "texte libre"}}
        {"answers": [{"question_id": 1, "choice_id": 4}]}
        {"answers": [{"question_id": 4, "answer_text": "texte libre"}]}

    La sortie normalisée est toujours de la forme :
        {"<question_id>": {"choices": [ids], "text": "..."}}

    Le score n'est jamais accepté depuis le client (spec §33 règle 2).
    """
    answers = serializers.JSONField(
        help_text="Réponses par identifiant de question (choix, liste de choix ou texte)."
    )
    attempt_id = serializers.IntegerField(required=False, allow_null=True)

    def _normalize_choice(self, value):
        if isinstance(value, list):
            try:
                return [int(item) for item in value]
            except (TypeError, ValueError):
                raise serializers.ValidationError('Les identifiants de choix doivent être numériques.')
        if isinstance(value, dict):
            return None
        try:
            return [int(value)]
        except (TypeError, ValueError):
            return []

    def validate_answers(self, value):
        normalized = {}

        if isinstance(value, dict):
            for question_id, raw in value.items():
                if isinstance(raw, dict):
                    normalized[str(question_id)] = {
                        'choices': self._normalize_choice(
                            raw.get('choice_ids', raw.get('choice_id', raw.get('choices', [])))
                        ) or [],
                        'text': str(raw.get('answer_text', raw.get('text', '')) or ''),
                    }
                elif isinstance(raw, list):
                    normalized[str(question_id)] = {
                        'choices': self._normalize_choice(raw) or [], 'text': ''
                    }
                else:
                    # Scalaire ambigu : un identifiant de choix (« 4 ») OU une
                    # valeur brute (« 60 » pour une question NUMERIC, du texte
                    # pour une réponse libre). On transmet les deux représentations
                    # et la correction choisit selon le type de la question.
                    choices = self._normalize_choice(raw)
                    normalized[str(question_id)] = {
                        'choices': choices or [],
                        'text': str(raw),
                    }
            return normalized

        if isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    raise serializers.ValidationError(
                        'Chaque réponse doit être un objet avec question_id et choice_id.'
                    )
                question_id = item.get('question_id')
                if question_id is None:
                    raise serializers.ValidationError('Chaque réponse doit contenir question_id.')
                choice_id = item.get('choice_id', item.get('choice_ids', item.get('choices')))
                answer_text = str(item.get('answer_text', item.get('text', '')) or '')
                if choice_id is None and not answer_text:
                    raise serializers.ValidationError(
                        'Chaque réponse doit contenir choice_id ou answer_text.'
                    )
                normalized[str(question_id)] = {
                    'choices': self._normalize_choice(choice_id) or [] if choice_id is not None else [],
                    'text': answer_text,
                }
            return normalized

        raise serializers.ValidationError('Le champ answers doit être un dictionnaire ou une liste d’objets.')
