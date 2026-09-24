# courses/serializers/quiz_serializer.py
"""Sérialiseurs du Learning & Assessment Engine (spec SCHOOL_ON_Learning_Quiz_Engine).

Règle de sécurité (spec §33, règle 3) :
le corrigé (`is_correct`, `correct_numeric`) ne doit JAMAIS être exposé à un
apprenant pendant qu'il passe un quiz. On distingue donc deux familles de
sérialiseurs :
    * ``*Learner*`` : destinés aux apprenants, le corrigé est masqué ;
    * ``*Staff*``   : destinés au créateur (mentor/admin) et aux actions de review.
"""
from rest_framework import serializers

from ..models import Quiz, Question, Choice, AttemptAnswer, QuizAttempt


class QuizChoiceLearnerSerializer(serializers.ModelSerializer):
    """Choix de réponse vu par l'apprenant : aucune information sur le corrigé."""
    class Meta:
        model = Choice
        fields = ['id', 'text', 'order']


class QuizChoiceStaffSerializer(serializers.ModelSerializer):
    """Choix de réponse vu par le créateur du contenu."""
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order']


class QuizQuestionLearnerSerializer(serializers.ModelSerializer):
    """Question telle qu'elle est présentée à l'apprenant (corrigé masqué)."""
    choices = QuizChoiceLearnerSerializer(many=True, read_only=True)
    type = serializers.CharField(source='question_type', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'type', 'points', 'order', 'choices']


class QuizQuestionStaffSerializer(serializers.ModelSerializer):
    """Question complète, corrigé inclus, pour le créateur et l'admin."""
    choices = QuizChoiceStaffSerializer(many=True, read_only=True)
    type = serializers.CharField(source='question_type', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'text', 'question_type', 'type', 'points', 'order',
            'correct_numeric', 'explanation', 'choices', 'created_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class QuizChoiceWriteSerializer(serializers.ModelSerializer):
    """Écriture d'un choix de réponse (utilisé à la création d'une question)."""
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'order']
        read_only_fields = ['id']

class QuizQuestionWriteSerializer(serializers.ModelSerializer):
    """Création / mise à jour d'une question, corrigé inclus (spec §12)."""
    choices = QuizChoiceWriteSerializer(many=True, required=False, default=list)

    class Meta:
        model = Question
        fields = [
            'id', 'text', 'question_type', 'points', 'order', 'correct_numeric',
            'explanation', 'choices',
        ]
        read_only_fields = ['id']

    def validate_choices(self, choices):
        if self.initial_data.get('question_type', 'SINGLE_CHOICE') == 'NUMERIC':
            return choices
        if not choices:
            raise serializers.ValidationError('Une question doit avoir au moins une réponse.')
        return choices

    def validate(self, attrs):
        """Valide la cohérence question_type <-> réponses (spec §12)."""
        instance = getattr(self, 'instance', None)
        question_type = attrs.get('question_type', getattr(instance, 'question_type', 'SINGLE_CHOICE'))
        choices = attrs.get('choices', None)
        if choices is None and instance is not None:
            choices = [
                {'text': c.text, 'is_correct': c.is_correct, 'order': c.order}
                for c in instance.choices.all()
            ]
        choices = choices or []

        if question_type == 'NUMERIC':
            correct_numeric = attrs.get('correct_numeric', getattr(instance, 'correct_numeric', None))
            if correct_numeric is None:
                raise serializers.ValidationError({'correct_numeric': 'La réponse numérique est obligatoire.'})
            return attrs

        correct_count = sum(1 for choice in choices if choice.get('is_correct'))
        if question_type in {'SINGLE_CHOICE', 'TRUE_FALSE'} and correct_count != 1:
            raise serializers.ValidationError(
                {'choices': 'Cette question doit avoir exactement une bonne réponse.'}
            )
        if question_type in {'SINGLE_CHOICE', 'TRUE_FALSE', 'MULTIPLE_CHOICE'} and len(choices) < 2:
            raise serializers.ValidationError({'choices': 'Cette question doit avoir au moins deux choix.'})
        if question_type == 'TRUE_FALSE' and len(choices) != 2:
            raise serializers.ValidationError({'choices': 'Une question Vrai/Faux doit avoir deux réponses.'})
        if question_type == 'MULTIPLE_CHOICE' and correct_count < 1:
            raise serializers.ValidationError({'choices': 'Un choix multiple doit avoir au moins une bonne réponse.'})
        return attrs

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        Choice.objects.bulk_create([
            Choice(question=question, **{'order': choice.get('order') or index, **choice})
            for index, choice in enumerate(choices_data, start=1)
        ])
        return question

    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if choices_data is not None:
            instance.choices.all().delete()
            Choice.objects.bulk_create([
                Choice(question=instance, **{'order': choice.get('order') or index, **choice})
                for index, choice in enumerate(choices_data, start=1)
            ])
        return instance



class AttemptAnswerSerializer(serializers.ModelSerializer):
    """Détail de correction d'une question pour une tentative (spec §33 règle 4)."""
    question_text = serializers.ReadOnlyField(source='question.text')
    question_type = serializers.ReadOnlyField(source='question.question_type')
    question_points = serializers.ReadOnlyField(source='question.points')
    explanation = serializers.ReadOnlyField(source='question.explanation')
    correct_choice_ids = serializers.SerializerMethodField()
    correct_numeric = serializers.DecimalField(
        source='question.correct_numeric', max_digits=12, decimal_places=4, read_only=True
    )

    class Meta:
        model = AttemptAnswer
        fields = [
            'id', 'question', 'question_text', 'question_type', 'question_points',
            'selected_choices', 'answer_text', 'is_correct', 'points_awarded',
            'correct_choice_ids', 'correct_numeric', 'explanation', 'answered_at',
        ]
        read_only_fields = fields

    def get_correct_choice_ids(self, obj):
        return list(obj.question.correct_choice_ids())


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Ligne d'historique des résultats (spec §22)."""
    quiz_title = serializers.ReadOnlyField(source='quiz.title')
    quiz_type = serializers.ReadOnlyField(source='quiz.quiz_type')
    percentage = serializers.FloatField(source='score', read_only=True)
    passed = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'quiz_type', 'score', 'percentage',
            'raw_score', 'max_score', 'correct_answers', 'wrong_answers',
            'status', 'passed', 'duration_seconds', 'started_at', 'submitted_at',
            'completed_at',
        ]
        read_only_fields = fields

    def get_passed(self, obj):
        return obj.is_passed()


class QuizAttemptDetailSerializer(QuizAttemptSerializer):
    """Tentative avec correction détaillée question par question (spec §33)."""
    answers = AttemptAnswerSerializer(many=True, read_only=True)

    class Meta(QuizAttemptSerializer.Meta):
        fields = QuizAttemptSerializer.Meta.fields + ['answers']


class QuizSerializer(serializers.ModelSerializer):
    """Lecture d'un quiz.

    Le jeu de champs est identique pour tous les rôles, mais le contenu des
    questions dépend du contexte :
    - ``include_answers=True`` (créateur / admin) : corrigé inclus ;
    - sinon (apprenant) : corrigé masqué.
    """
    questions = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField(source='category.name')
    course_title = serializers.ReadOnlyField(source='course.title')
    questions_count = serializers.IntegerField(read_only=True)
    max_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'course', 'course_title', 'chapter', 'category', 'category_name',
            'title', 'description', 'quiz_type', 'subject', 'level', 'school_level',
            'year', 'session', 'series', 'duration', 'shuffle_questions',
            'shuffle_choices', 'random_question_count', 'allow_multiple_attempts',
            'max_attempts', 'passing_score', 'status', 'review_note', 'xp_reward',
            'questions_count', 'max_score', 'created_at', 'updated_at', 'questions',
        ]

    def get_questions(self, obj):
        questions = obj.questions.all().prefetch_related('choices')
        if self._include_answers(obj):
            return QuizQuestionStaffSerializer(questions, many=True).data
        return QuizQuestionLearnerSerializer(questions, many=True).data

    def _include_answers(self, obj):
        """Le corrigé n'est visible que par le créateur et l'administration."""
        explicit = self.context.get('include_answers')
        if explicit is not None:
            return bool(explicit)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or obj.created_by_id == user.id:
            return True
        return bool(obj.course_id and obj.course.teacher_id == user.id)

