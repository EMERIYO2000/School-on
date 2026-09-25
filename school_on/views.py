from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        database_status = 'ok'
        http_status = 200
    except Exception:
        database_status = 'error'
        http_status = 503

    payload = {
        'status': 'ok' if database_status == 'ok' else 'degraded',
        'service': 'school_on',
        'database': database_status,
        'timestamp': timezone.now().isoformat(),
    }
    return JsonResponse(payload, status=http_status)
