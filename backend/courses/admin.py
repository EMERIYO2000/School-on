from django.contrib import admin
from django.utils import timezone
from .models import (
    Category, StateExam, ExamQuestion, ExamChoice, ArchiveResource, Course, Chapter, Lesson,
    Quiz, Question, Choice, Enrollment, 
    LessonProgress, QuizAttempt
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'teacher', 'status', 'reviewed_by', 'is_published')
    list_filter = ('status', 'is_published', 'is_premium', 'is_state_exam_prep', 'level', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('reviewed_by', 'reviewed_at')
    actions = ('approve_courses', 'send_back_courses')

    @admin.action(description='Accepter les cours sélectionnés')
    def approve_courses(self, request, queryset):
        queryset.update(status='PUBLISHED', is_published=True, reviewed_by=request.user, reviewed_at=timezone.now(), review_note='')

    @admin.action(description='Renvoyer les cours sélectionnés en brouillon')
    def send_back_courses(self, request, queryset):
        queryset.update(status='DRAFT', is_published=False, reviewed_by=request.user, reviewed_at=timezone.now())


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'xp_reward')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    inlines = [ChoiceInline]


class ExamChoiceInline(admin.TabularInline):
    model = ExamChoice
    extra = 2


class ExamQuestionInline(admin.StackedInline):
    model = ExamQuestion
    extra = 1
    inlines = [ExamChoiceInline]


@admin.register(StateExam)
class StateExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'subject', 'creator', 'status', 'created_at')
    list_filter = ('status', 'year', 'subject')
    search_fields = ('title', 'subject', 'creator__email')
    inlines = [ExamQuestionInline]


admin.site.register(Category)
admin.site.register(Chapter)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(QuizAttempt)
admin.site.register(ArchiveResource)