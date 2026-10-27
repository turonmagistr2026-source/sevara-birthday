from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
HTML_FILE = ROOT / "index.html"

print("SEVARA SITE — QUALITY CHECK")
print("=" * 36)

errors = []

def check(condition, success, failure):
    if condition:
        print(f"[PASS] {success}")
    else:
        print(f"[FAIL] {failure}")
        errors.append(failure)

check(HTML_FILE.is_file(), "HTML fayli mavjud", "HTML fayli topilmadi")

if not HTML_FILE.is_file():
    sys.exit(1)

html = HTML_FILE.read_text(encoding="utf-8")
check(bool(re.search(r'<html[^>]*lang=["\']uz["\']', html, re.I)),
      "O'zbek tili belgilangan", "HTML til atributi noto'g'ri yoki yo'q")
check(bool(re.search(r'<title>.*?</title>', html, re.I | re.S)),
      "Sahifa sarlavhasi mavjud", "Sahifa sarlavhasi topilmadi")
check("Sevara" in html, "Sevara nomi mavjud", "Sevara nomi topilmadi")

images = re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', html, re.I)
check(len(images) >= 3, "Kamida uchta rasm elementi mavjud",
      "Uchta rasm elementi topilmadi")

missing_images = []
for src in images:
    if re.match(r'^(https?:|data:|//)', src, re.I):
        continue
    path = (ROOT / src).resolve()
    if not path.is_file():
        missing_images.append(src)

check(not missing_images, "Mahalliy rasmlar topildi",
      "Topilmagan rasmlar: " + ", ".join(missing_images))

ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', html))
check(len(ids) >= 5, f"HTML IDlari mavjud ({len(ids)} ta)",
      "HTML IDlari yetarli emas")

links = re.findall(r'<(?:script|link)\b[^>]*\b(?:src|href)=["\']([^"\']+)["\']', html, re.I)
missing_links = []
for link in links:
    if link.startswith(("#", "https://", "http://", "//", "data:", "mailto:", "tel:")):
        continue
    path = (ROOT / link.split("?", 1)[0].split("#", 1)[0]).resolve()
    if not path.is_file():
        missing_links.append(link)

check(not missing_links, "Mahalliy CSS/JS havolalari tekshirildi",
      "Topilmagan fayllar: " + ", ".join(missing_links))

print("-" * 36)
print(f"HTML hajmi: {HTML_FILE.stat().st_size:,} bayt")
print(f"Topilgan IDlar: {len(ids)}")
print(f"Rasm elementlari: {len(images)}")
print("NATIJA:", "barcha tekshiruvlar muvaffaqiyatli!" if not errors else "tekshiruvda muammolar topildi.")
sys.exit(1 if errors else 0)
