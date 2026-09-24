from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, 
    TutorProfile, 
    ParentProfile, 
    TeacherApplication, 
    ParentChildRelation, 
    TutorRelationship
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
            
            TutorProfile.objects.get_or_create(
                user=user,
                defaults={'bio': app.bio, 'skills': app.skills}
            )

    @admin.action(description="Rejeter les candidatures sélectionnées")
    def reject_application(self, request, queryset):
        queryset.update(status='rejected')


admin.site.register(TutorProfile)
admin.site.register(ParentProfile)
admin.site.register(ParentChildRelation)
admin.site.register(TutorRelationship)