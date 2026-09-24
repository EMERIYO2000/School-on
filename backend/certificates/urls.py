from django.urls import path

from .views import CertificateDetailView, CertificateDownloadView, CertificateSignatureView, CertificationStatusView, FinalProjectView, MentorCertificationApprovalView, MyCertificatesView, VerifyCertificateView

urlpatterns = [
    path('', MyCertificatesView.as_view(), name='my-certificates'),
    path('<str:certificate_id>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('<str:certificate_id>/download/', CertificateDownloadView.as_view(), name='certificate-download'),
    path('<str:certificate_id>/signature/', CertificateSignatureView.as_view(), name='certificate-signature'),
    path('verify/<str:certificate_id>/', VerifyCertificateView.as_view(), name='verify-certificate'),
    path('courses/<int:course_id>/status/', CertificationStatusView.as_view(), name='certification-status'),
    path('courses/<int:course_id>/final-project/', FinalProjectView.as_view(), name='final-project'),
    path('courses/<int:course_id>/students/<int:student_id>/approve/', MentorCertificationApprovalView.as_view(), name='mentor-certification-approval'),
]
