import os
import platform
import datetime
from pydub import AudioSegment
from fpdf import FPDF
from docx import Document


def setup_ffmpeg():
    """Configura i percorsi di FFmpeg"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(base_dir)
    system_platform = platform.system()
    binary_ext = ".exe" if system_platform == "Windows" else ""

    ffmpeg_path = os.path.join(base_dir, f"ffmpeg{binary_ext}")
    ffprobe_path = os.path.join(base_dir, f"ffprobe{binary_ext}")

    os.environ["PATH"] += os.pathsep + base_dir

    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    return ffmpeg_path, ffprobe_path


def get_transcripts_folder():
    """Restituisce il percorso della cartella 'Sbobinature', creandola se non c'è"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, "Sbobinature")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return "{:d}:{:02d}:{:05.2f}".format(int(h), int(m), s)
    else:
        return "{:02d}:{:05.2f}".format(int(m), s)


def hms_to_seconds(hms_str):
    try:
        parts = hms_str.split(':')
        seconds = 0.0
        for part in parts: seconds = seconds * 60 + float(part)
        return seconds
    except ValueError:
        return 0.0


# --- EXPORT FUNCTIONS (Aggiornate per salvare nella stessa cartella del txt) ---

def save_as_pdf(text, original_txt_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, f"Trascrizione: {os.path.basename(original_txt_path)}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)

    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)

    # Salva nella stessa cartella del file txt (Sbobinature)
    output_path = original_txt_path.replace(".txt", ".pdf")
    pdf.output(output_path)
    return output_path


def save_as_docx(text, original_txt_path):
    doc = Document()
    doc.add_heading(f'Trascrizione: {os.path.basename(original_txt_path)}', 0)
    for paragraph in text.split('\n'):
        if paragraph.strip(): doc.add_paragraph(paragraph)

    output_path = original_txt_path.replace(".txt", ".docx")
    doc.save(output_path)
    return output_path


def save_as_reminder(text, original_txt_path):
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    start_time = tomorrow.strftime("%Y%m%dT100000")
    end_time = tomorrow.strftime("%Y%m%dT110000")

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sbobinator//App//IT
BEGIN:VEVENT
UID:{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}@sbobinator
DTSTAMP:{datetime.datetime.now().strftime("%Y%m%dT%H%M%S")}
DTSTART:{start_time}
DTEND:{end_time}
SUMMARY:Revisione: {os.path.basename(original_txt_path)}
DESCRIPTION:Ricordati di leggere la trascrizione salvata.
END:VEVENT
END:VCALENDAR"""

    output_path = original_txt_path.replace(".txt", ".ics")
    with open(output_path, "w") as f: f.write(ics_content)
    return output_path