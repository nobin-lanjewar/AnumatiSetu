"""
documents/precheck.py  -  real GST certificate pre-check for AnumatiSetu.

What it does (all computed from the uploaded file, nothing hard-coded):
  1. Extracts text: PDF text layer first (pdfplumber), OCR fallback (pytesseract)
     for scanned PDFs and images.
  2. Finds the GSTIN and validates it: 15-char format, embedded PAN format,
     state code, and the official check-digit.
  3. Finds the legal name and compares it with the business profile.
  4. Returns a result dict the template can show in your existing popup.

Install:
    pip install pdfplumber pytesseract pillow pymupdf
    # OCR also needs the Tesseract program installed on the machine
    # (Windows: UB Mannheim installer, Linux: apt install tesseract-ocr)

Use in a Django view:
    from documents.precheck import precheck_gst_certificate
    result = precheck_gst_certificate(doc.file.path,
                                      profile_name=business.legal_name,
                                      expected_state_code="27")
    # result["score"], result["status"], result["checks"], result["advisory"]
"""
import difflib
import re
from pathlib import Path

GSTIN_RE = re.compile(r"\b(\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b")
PAN_RE = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")
NAME_RE = re.compile(r"Legal\s+Name\s*[:\-]?\s*(.+)", re.IGNORECASE)
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Valid GST state codes (01-38, 97, 99). 27 = Maharashtra.
VALID_STATE_CODES = {f"{i:02d}" for i in range(1, 39)} | {"97", "99"}


# ---------- 1. text extraction ----------
def extract_text(path):
    """Return (text, source) where source is 'pdf-text', 'ocr' or 'none'."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
            if len(text.strip()) > 30:
                return text, "pdf-text"
        except Exception:
            pass
        # Scanned PDF: render pages to images and OCR them.
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io
            parts = []
            with fitz.open(path) as doc:
                for page in doc:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    parts.append(pytesseract.image_to_string(img))
            text = "\n".join(parts)
            return text, ("ocr" if text.strip() else "none")
        except Exception:
            return "", "none"

    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}:
        try:
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(path))
            return text, ("ocr" if text.strip() else "none")
        except Exception:
            return "", "none"

    return "", "none"


# ---------- 2. GSTIN validation ----------
def gstin_check_digit(first14):
    """Official GSTIN checksum (base-36, alternating weights 1 and 2)."""
    total = 0
    for i, ch in enumerate(first14):
        value = CHARS.index(ch) * (1 if i % 2 == 0 else 2)
        total += value // 36 + value % 36
    return CHARS[(36 - total % 36) % 36]


def validate_gstin(gstin):
    """Return a list of (name, passed, detail) checks for one GSTIN."""
    checks = []
    fmt_ok = bool(GSTIN_RE.fullmatch(gstin))
    checks.append(("GSTIN format (15 characters)", fmt_ok, gstin))
    if not fmt_ok:
        return checks
    checks.append(("Embedded PAN format", bool(PAN_RE.match(gstin[2:12])), gstin[2:12]))
    checks.append(("State code valid", gstin[:2] in VALID_STATE_CODES, gstin[:2]))
    checks.append(("GSTIN check digit", gstin_check_digit(gstin[:14]) == gstin[14],
                   "last character must be " + gstin_check_digit(gstin[:14])))
    return checks


# ---------- 3. main entry point ----------
def precheck_gst_certificate(path, profile_name=None, expected_state_code="27"):
    text, source = extract_text(path)
    upper = text.upper()
    checks = []

    checks.append(("Readable text found", source != "none",
                   {"pdf-text": "digital PDF text layer", "ocr": "read with OCR",
                    "none": "no text could be read"}[source]))

    match = GSTIN_RE.search(upper.replace(" ", ""))
    gstin = match.group(1) if match else None
    if gstin:
        checks.extend(validate_gstin(gstin))
        checks.append((f"State code is {expected_state_code} (Maharashtra)",
                       gstin[:2] == expected_state_code, gstin[:2]))
    else:
        checks.append(("GSTIN found in document", False, "no 15-character GSTIN detected"))

    name_match = NAME_RE.search(text)
    doc_name = name_match.group(1).strip() if name_match else None
    checks.append(("Legal name found", bool(doc_name), doc_name or "not detected"))
    if doc_name and profile_name:
        ratio = difflib.SequenceMatcher(None, doc_name.upper(), profile_name.upper()).ratio()
        checks.append(("Name matches business profile", ratio >= 0.85,
                       f"similarity {ratio:.0%} with '{profile_name}'"))

    passed = sum(1 for _, ok, _ in checks if ok)
    score = round(100 * passed / len(checks), 1)
    failed = [name for name, ok, _ in checks if not ok]

    return {
        "status": "Pre-validated" if not failed else "Needs attention",
        "score": score,  # share of checks passed, not an OCR confidence
        "text_source": source,
        "gstin": gstin,
        "legal_name": doc_name,
        "checks": [{"name": n, "passed": ok, "detail": d} for n, ok, d in checks],
        "advisory": ("Verify that the registered unit address matches the MIDC plot allotment."
                     if not failed else "Fix before submission: " + "; ".join(failed)),
        "disclaimer": "Advisory check only. Final scrutiny rests with the concerned authority.",
    }


if __name__ == "__main__":
    import sys
    import json
    print(json.dumps(precheck_gst_certificate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None),
                     indent=2))
