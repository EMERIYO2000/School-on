from io import BytesIO
from pathlib import Path
import textwrap

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


def _fit_font(draw, text, max_width, size=22, bold=False, minimum=10):
    while size > minimum and draw.textbbox((0, 0), text, font=_font(size, bold=bold))[2] > max_width:
        size -= 1
    return _font(size, bold=bold)


def _centered_wrapped(draw, text, center, y, max_width, font, fill, line_gap=4):
    words = str(text or '').split()
    lines = []
    current = ''
    for word in words:
        candidate = f'{current} {word}'.strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    line_height = font.getbbox('Ag')[3] - font.getbbox('Ag')[1]
    for index, line in enumerate(lines):
        draw.text((center, y + index * (line_height + line_gap)), line, fill=fill, font=font, anchor='ma')
    return y + max(1, len(lines)) * (line_height + line_gap)


def render_certificate_pdf(certificate):
    if TEMPLATE_PATH.exists():
        template = Image.open(TEMPLATE_PATH).convert('RGB')
        width, height = template.size
        canvas = Image.new('RGB', (width, height), 'white')
        canvas.paste(template, (0, 0))
    else:
        width, height = 1600, 1100
        canvas = Image.new('RGB', (width, height), '#f8fafc')
        fallback_draw = ImageDraw.Draw(canvas)
        fallback_draw.rectangle((24, 24, width - 24, height - 24), outline='#d6b36a', width=8)
        fallback_draw.rectangle((48, 48, width - 48, height - 48), outline='#17324d', width=2)
        fallback_draw.line((100, 170, width - 100, 170), fill='#d6b36a', width=3)
    draw = ImageDraw.Draw(canvas)

    # The template remains the visual source; these fields make each PDF identifiable.
    text_color = '#1f2937'
    center = width // 2
    date_font = _font(10)
    start_date = certificate.study_started_at.strftime('%d/%m/%Y') if certificate.study_started_at else '—'
    end_date = certificate.study_completed_at.strftime('%d/%m/%Y') if certificate.study_completed_at else '—'
    public_base_url = getattr(settings, 'CERTIFICATE_PUBLIC_BASE_URL', 'http://localhost:3000').rstrip('/')
    verification_url = f'{public_base_url}/certificate/{certificate.certificate_id}'
    qr_image = qrcode.make(verification_url).convert('RGB').resize((110, 110))
    student_signature = certificate.student_signature_text or certificate.student_name
    draw.text((center, int(height * 0.22)), 'CERTIFICAT DE RÉUSSITE', fill='#17324d', font=_font(24, True), anchor='mm')
    draw.text((center, int(height * 0.29)), 'SCHOOL ON', fill='#b36b3f', font=_font(11, True), anchor='mm')
    draw.text((center, int(height * 0.46)), 'Décerné à', fill='#64748b', font=_font(10), anchor='mm')
    draw.text((center, int(height * 0.51)), certificate.student_name, fill=text_color, font=_fit_font(draw, certificate.student_name, int(width * 0.70), 24, True), anchor='mm')
    _centered_wrapped(draw, certificate.course_title, center, int(height * 0.60), int(width * 0.64), _fit_font(draw, certificate.course_title, int(width * 0.64), 16, True), text_color)
    draw.text((center, int(height * 0.70)), f'Parcours suivi : {start_date} - {end_date}', fill=text_color, font=date_font, anchor='mm')
    draw.line((int(width * 0.12), int(height * 0.75), int(width * 0.88), int(height * 0.75)), fill='#d6b36a', width=2)
    draw.text((int(width * 0.25), int(height * 0.81)), student_signature, fill=text_color, font=_fit_font(draw, student_signature, int(width * 0.28), 12, True), anchor='mm')
    draw.text((int(width * 0.25), int(height * 0.86)), 'Signature apprenant', fill='#64748b', font=_font(8), anchor='mm')
    if OFFICIAL_SIGNATURE_PATH.exists():
        official_signature = Image.open(OFFICIAL_SIGNATURE_PATH).convert('RGBA')
        official_signature.thumbnail((130, 45))
        canvas.paste(official_signature, (int(width * 0.58), int(height * 0.76)), official_signature)
    draw.text((int(width * 0.65), int(height * 0.86)), 'Signature SCHOOL ON', fill='#64748b', font=_font(8), anchor='mm')
    draw.text((center, int(height * 0.94)), certificate.certificate_id, fill='#64748b', font=_font(9), anchor='mm')
    qr_x, qr_y = width - 126, height - 126
    draw.rectangle((qr_x - 6, qr_y - 6, qr_x + 116, qr_y + 116), fill='white', outline='#d6b36a', width=2)
    canvas.paste(qr_image, (qr_x, qr_y))

    output = BytesIO()
    canvas.save(output, format='PDF', resolution=150.0, title=f'Certificat {certificate.certificate_id}')
    output.seek(0)
    return output
