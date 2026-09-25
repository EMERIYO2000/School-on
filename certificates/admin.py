from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'course', 'status', 'issued_at')
    search_fields = ('certificate_id', 'student__email', 'course__title')
    list_filter = ('status',)
