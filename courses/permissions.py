# courses/permissions.py
"""Permissions partagées du Learning & Assessment Engine."""
from rest_framework import permissions


def user_can_edit_quiz(user, quiz):
    """Vrai si l'utilisateur peut modifier un quiz et son contenu.

    - l'administration peut tout modifier ;
    - le créateur du quiz peut le modifier ;
    - le mentor propriétaire du cours peut modifier ses quiz ;
    - un quiz autonome (Game / Training) n'est modifiable que par son créateur.
    """
    if not user or not user.is_authenticated or quiz is None:
        return False
    if user.is_staff:
        return True
    if quiz.created_by_id == user.id:
        return True
    return bool(quiz.course_id and quiz.course.teacher_id == user.id)


def user_can_edit_course(user, course):
    """Vrai si l'utilisateur peut modifier un cours (mentor propriétaire ou admin)."""
    if not user or not user.is_authenticated or course is None:
        return False
    return bool(user.is_staff or course.teacher_id == user.id)


class IsCourseOwnerOrAdmin(permissions.BasePermission):
    """Accès en écriture réservé au mentor propriétaire du cours ou à l'admin."""
    message = "Vous ne pouvez modifier que vos propres cours."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        course = getattr(obj, 'course', obj)
        return user_can_edit_course(request.user, course)
