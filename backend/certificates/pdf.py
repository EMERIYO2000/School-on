from io import BytesIO
from pathlib import Path

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import qrcode


TEMPLATE_PATH = (
    Path(settings.BASE_DIR).parent
    / 'Project_School_On_v1'
    / '.kombai'
    / 'design-systems'
    / 'template'
    / 'certificat_exemp.jfif'
)
OFFICIAL_SIGNATURE_PATH = Path(settings.BASE_DIR).parent / 'signature.png'


def _font(size, bold=False):
    candidates = [
        'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/calibrib.ttf' if bold else 'C:/Windows/Fonts/calibri.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render_certificate_pdf(certificate):
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f'Modèle de certificat introuvable: {TEMPLATE_PATH}')

    template = Image.open(TEMPLATE_PATH).convert('RGB')
    width, height = template.size
    canvas = Image.new('RGB', (width, height), 'white')
    canvas.paste(template, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # The template remains the visual source; these fields make each PDF identifiable.
    text_color = '#1f2937'
    center = width // 2
    date_font = _font(10)
    start_date = certificate.study_started_at.strftime('%d/%m/%Y') if certificate.study_started_at else '—'
    end_date = certificate.study_completed_at.strftime('%d/%m/%Y') if certificate.study_completed_at else '—'
    public_base_url = getattr(settings, 'CERTIFICATE_PUBLIC_BASE_URL', 'http://localhost:3000').rstrip('/')
    verification_url = f'{public_base_url}/verify/{certificate.certificate_id}'
    qr_image = qrcode.make(verification_url).convert('RGB').resize((92, 92))
    student_signature = certificate.student_signature_text or certificate.student_name
    draw.text((center, int(height * 0.52)), certificate.student_name, fill=text_color, font=_font(22, True), anchor='mm')
    draw.text((center, int(height * 0.62)), certificate.course_title, fill=text_color, font=_font(16, True), anchor='mm')
    draw.text((center, int(height * 0.72)), f'Études : {start_date} - {end_date}', fill=text_color, font=date_font, anchor='mm')
    draw.text((int(width * 0.25), int(height * 0.80)), student_signature, fill=text_color, font=_font(12, True), anchor='mm')
    draw.text((int(width * 0.25), int(height * 0.84)), 'Signature apprenant', fill=text_color, font=_font(8), anchor='mm')
    if OFFICIAL_SIGNATURE_PATH.exists():
        official_signature = Image.open(OFFICIAL_SIGNATURE_PATH).convert('RGBA')
        official_signature.thumbnail((130, 45))
        canvas.paste(official_signature, (int(width * 0.58), int(height * 0.76)), official_signature)
    draw.text((int(width * 0.65), int(height * 0.84)), 'Signature SCHOOL ON', fill=text_color, font=_font(8), anchor='mm')
    draw.text((center, int(height * 0.88)), certificate.certificate_id, fill=text_color, font=_font(10), anchor='mm')
    canvas.paste(qr_image, (width - 112, height - 112))

    output = BytesIO()
    canvas.save(output, format='PDF', resolution=150.0, title=f'Certificat {certificate.certificate_id}')
    output.seek(0)
    return output
