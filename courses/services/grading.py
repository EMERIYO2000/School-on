# courses/services/grading.py
"""Correction automatique du Question Engine (spec §17, §18 et §33).

Le concepteur définit le corrigé une seule fois (`Choice.is_correct`,
`Question.correct_numeric`). Ce module applique ce corrigé aux tentatives des
apprenants. Aucune intervention humaine n'est nécessaire pour les types
``SINGLE_CHOICE``, ``MULTIPLE_CHOICE``, ``TRUE_FALSE`` et ``NUMERIC``.
"""
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.utils import timezone


@dataclass
class GradedAnswer:
    """Résultat de correction d'une question."""
    question: object
    is_correct: bool
    points_awarded: Decimal
    selected_choices: list = field(default_factory=list)
    answer_text: str = ''


@dataclass
class GradedAttempt:
    """Résultat complet d'une tentative."""
    answers: list = field(default_factory=list)
    raw_score: Decimal = Decimal('0')
    max_score: Decimal = Decimal('0')
    percentage: float = 0.0
    correct_answers: int = 0
    wrong_answers: int = 0

    @property
    def details(self):
        return [
            {
                'question_id': item.question.id,
                'is_correct': item.is_correct,
                'points_awarded': float(item.points_awarded),
                'explanation': item.question.explanation or '',
                'question_type': item.question.question_type,
            }
            for item in self.answers
        ]


def _clamp_numeric(value):
    try:
        return Decimal(str(value).strip().replace(',', '.'))
    except (InvalidOperation, TypeError, ValueError, AttributeError):
        return None


def grade_question(question, submitted):
    """Corrige une question unique.

    ``submitted`` est un dictionnaire ``{'choices': [ids], 'text': str}``
    (voir ``QuizSubmitSerializer``). Retourne un :class:`GradedAnswer`.
    """
    selected_ids = list(submitted.get('choices') or [])
    answer_text = str(submitted.get('text') or '').strip()
    correct_ids = question.correct_choice_ids()
    question_type = question.question_type
    is_correct = False

    if question_type in {'SINGLE_CHOICE', 'TRUE_FALSE', 'MULTIPLE_CHOICE'}:
        selected = {int(choice_id) for choice_id in selected_ids if str(choice_id).isdigit()}
        # V1 : tout ou rien — toutes les bonnes réponses et aucune mauvaise (spec §10.2).
        is_correct = bool(correct_ids) and selected == correct_ids

    elif question_type == 'NUMERIC':
        submitted_number = _clamp_numeric(answer_text)
        expected = question.correct_numeric
        is_correct = submitted_number is not None and expected is not None and submitted_number == expected

    else:
        # FREE_TEXT n'entre pas dans la correction automatique de la V1 (spec §11).
        is_correct = False

    return GradedAnswer(
        question=question,
        is_correct=is_correct,
        points_awarded=Decimal(question.points) if is_correct else Decimal('0'),
        selected_choices=[int(choice_id) for choice_id in selected_ids if str(choice_id).isdigit()],
        answer_text=answer_text,
    )


def grade_attempt(questions, user_answers):
    """Corrige une tentative complète.

    :param questions: itérable de :class:`~courses.models.Question`
    :param user_answers: ``{'<question_id>': {'choices': [...], 'text': '...'}}``
    :returns: :class:`GradedAttempt` avec score brut, score maximum et pourcentage.
    """
    result = GradedAttempt()
    for question in questions:
        submitted = user_answers.get(str(question.id)) or user_answers.get(question.id) or {}
        if not isinstance(submitted, dict):
            submitted = {'choices': [], 'text': str(submitted)}
        graded = grade_question(question, submitted)
        result.answers.append(graded)
        result.max_score += Decimal(question.points)
        if graded.is_correct:
            result.correct_answers += 1
            result.raw_score += graded.points_awarded
        else:
            result.wrong_answers += 1

    if result.max_score:
        result.percentage = round((float(result.raw_score) / float(result.max_score)) * 100, 2)
    return result


def build_attempt_answers(attempt, graded_attempt):
    """Prépare les lignes ``AttemptAnswer`` à enregistrer pour une tentative."""
    from ..models import AttemptAnswer

    return [
        AttemptAnswer(
            attempt=attempt,
            question=item.question,
            selected_choices=item.selected_choices,
            answer_text=item.answer_text,
            is_correct=item.is_correct,
            points_awarded=item.points_awarded,
        )
        for item in graded_attempt.answers
    ]


def attempt_duration(attempt):
    """Durée effective de la tentative en secondes (le serveur fait foi)."""
    end = attempt.submitted_at or timezone.now()
    return max(0, int((end - attempt.started_at).total_seconds()))
