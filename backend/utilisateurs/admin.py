from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    TutorProfile, 
    ParentProfile, 
    TeacherApplication, 
    ParentChildRelation, 
    TutorRelationship,
    LearnerProfile,
    MentorApplication,
    MentorSkill,
    Qualification,
    VerificationRecord,
    MentorAssessment,
    MentorInterview,
    MentorReport,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_teacher', 'is_parent', 'is_premium_subscriber', 'is_staff')
    list_filter = ('user_type', 'is_teacher', 'is_parent', 'is_premium_subscriber', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations SCHOOL ON', {
            'fields': ('user_type', 'phone_number', 'avatar', 'is_teacher', 'is_parent', 'is_premium_subscriber', 'latitude', 'longitude', 'fcm')
        }),
    )


@admin.register(TeacherApplication)
class TeacherApplicationAdmin(admin.ModelAdmin):
    """Validation des candidatures enseignants avec création automatique du profil pro[cite: 13]."""
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['approve_application', 'reject_application']

    @admin.action(description="Approuver et convertir en Enseignant/Mentor")
    def approve_application(self, request, queryset):
        for app in queryset.filter(status='pending'):
            app.status = 'approved'
            app.save()
            
            user = app.user
            user.is_teacher = True
            user.user_type = 'TEACHER'
            user.save()
            
            tutor_profile, _ = TutorProfile.objects.get_or_create(
                user=user,
                defaults={'bio': app.bio, 'skills': app.skills}
            )
            # Synchronisation avec le parcours de vérification mentor (spec §26).
            tutor_profile.mentor_status = 'VERIFIED'
            tutor_profile.is_verified = True
            tutor_profile.save(update_fields=['mentor_status', 'is_verified'])
            MentorApplication.objects.filter(user=user).exclude(
                status__in=['VERIFIED', 'SUSPENDED']
            ).update(status='VERIFIED')

    @admin.action(description="Rejeter les candidatures sélectionnées")
    def reject_application(self, request, queryset):
        queryset.update(status='rejected')


@admin.register(MentorApplication)
class MentorApplicationAdmin(admin.ModelAdmin):
    """File de review des candidatures mentor (spec §30 et §31)."""
    list_display = ('id', 'user', 'status', 'city', 'submitted_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'country', 'submitted_at')
    search_fields = ('user__email', 'user__username', 'legal_name', 'city')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'reviewed_at', 'reviewed_by')
    actions = ['approve_applications', 'reject_applications', 'request_information']

    @admin.action(description="Approuver les candidatures sélectionnées (mentors vérifiés)")
    def approve_applications(self, request, queryset):
        from django.utils import timezone as tz

        for application in queryset:
            application.status = 'VERIFIED'
            application.reviewed_at = tz.now()
            application.reviewed_by = request.user
            application.save()
            profile, _ = TutorProfile.objects.get_or_create(user=application.user)
            profile.mentor_status = 'VERIFIED'
            profile.is_verified = True
            profile.verified_at = tz.now()
            profile.save(update_fields=['mentor_status', 'is_verified', 'verified_at'])
            application.user.is_teacher = True
            application.user.user_type = 'TEACHER'
            application.user.save(update_fields=['is_teacher', 'user_type'])
            VerificationRecord.objects.create(
                application=application,
                mentor=application.user,
                verification_type='STATUS',
                status='PASSED',
                reviewed_by=request.user,
                reviewed_at=tz.now(),
                reason='Approuvé depuis l’administration Django.',
            )

    @admin.action(description="Rejeter les candidatures sélectionnées")
    def reject_applications(self, request, queryset):
        from django.utils import timezone as tz

        queryset.update(status='REJECTED', reviewed_at=tz.now(), reviewed_by=request.user)
        TutorProfile.objects.filter(user__in=queryset.values('user')).update(
            mentor_status='REJECTED', is_verified=False
        )

    @admin.action(description="Demander des informations complémentaires")
    def request_information(self, request, queryset):
        from django.utils import timezone as tz

        queryset.update(status='NEEDS_INFORMATION', reviewed_at=tz.now(), reviewed_by=request.user)
        TutorProfile.objects.filter(user__in=queryset.values('user')).update(
            mentor_status='NEEDS_INFORMATION'
        )


@admin.register(VerificationRecord)
class VerificationRecordAdmin(admin.ModelAdmin):
    """Historique traçable des décisions (spec §31)."""
    list_display = ('id', 'application', 'mentor', 'verification_type', 'status', 'reviewed_by', 'reviewed_at')
    list_filter = ('verification_type', 'status', 'reviewed_at')
    search_fields = ('mentor__email', 'mentor__username', 'reason', 'notes')
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by')


@admin.register(MentorReport)
class MentorReportAdmin(admin.ModelAdmin):
    """Signalements de mentors (spec §32 et §33)."""
    list_display = ('id', 'mentor', 'reporter', 'reason', 'status', 'created_at', 'reviewed_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('mentor__email', 'reporter__email', 'details')
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by')


class MentorSkillInline(admin.TabularInline):
    model = MentorSkill
    extra = 1


class QualificationInline(admin.TabularInline):
    model = Qualification
    extra = 1


class VerificationRecordInline(admin.TabularInline):
    model = VerificationRecord
    extra = 0
    readonly_fields = ('verification_type', 'status', 'reviewed_by', 'reviewed_at', 'reason', 'notes')


MentorApplicationAdmin.inlines = [MentorSkillInline, QualificationInline, VerificationRecordInline]


admin.site.register(TutorProfile)
admin.site.register(LearnerProfile)
admin.site.register(ParentProfile)
admin.site.register(ParentChildRelation)
admin.site.register(TutorRelationship)
admin.site.register(MentorAssessment)
admin.site.register(MentorInterview)