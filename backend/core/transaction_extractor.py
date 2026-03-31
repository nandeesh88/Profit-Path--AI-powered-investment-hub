import hashlib
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Optional, Tuple


DATE_PATTERNS = [
    r"\d{2}[/\s-]\d{2}[/\s-]\d{4}",
    r"\d{4}[/\s-]\d{2}[/\s-]\d{2}",
    r"\d{2}\s+[A-Za-z]{3,9}\s+\d{4}",
    r"\d{2}[/\s-]\d{2}[/\s-]\d{2}",
]

AMOUNT_PATTERN = re.compile(
    r"(?:INR|Rs\.?|₹)?\s*([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{1,2}|[0-9]+\.[0-9]{1,2})",
    re.IGNORECASE,
)

REFERENCE_PATTERN = re.compile(
    r"(?:UTR|Ref(?:erence)?(?:\s*ID)?|Txn(?:\s*ID)?|Transaction\s*ID)\s*[:#-]?\s*([A-Za-z0-9-]{6,})",
    re.IGNORECASE,
)

MERCHANT_HINT_PATTERN = re.compile(
    r"(?:to|at|merchant|receiver|beneficiary)\s*[:\-]?\s*([A-Za-z0-9 .&'-]{3,80})",
    re.IGNORECASE,
)

DEBIT_WORDS = {"debit", "dr", "withdrawal", "paid", "purchase", "upi"}
CREDIT_WORDS = {"credit", "cr", "salary", "refund", "deposit", "received"}


@dataclass
class ExtractedTransaction:
    amount: float
    transaction_date: str
    merchant_name: str
    transaction_type: str
    bank_reference_id: Optional[str]
    source_line: str


@dataclass
class ExtractionResult:
    raw_text: str
    transactions: List[ExtractedTransaction]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_date_safe(value: str) -> Optional[date]:
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%d/%m/%y", "%d-%m-%y", "%d %m %Y", "%d %m %y"]
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _extract_first_date(text: str) -> Optional[date]:
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if not match:
            continue
        parsed = parse_date_safe(match.group(0))
        if parsed:
            return parsed
    return None


def _extract_amounts(text: str) -> List[float]:
    values: List[float] = []
    for match in AMOUNT_PATTERN.findall(text):
        try:
            amount = Decimal(match.replace(",", ""))
            if amount > 0:
                values.append(float(amount))
        except (InvalidOperation, ValueError):
            continue
    return values


def _normalize_lines(text: str) -> List[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _looks_like_credit(line_lower: str) -> bool:
    return any(word in line_lower for word in CREDIT_WORDS) and not any(word in line_lower for word in DEBIT_WORDS)


def _extract_reference_id(text: str) -> Optional[str]:
    match = REFERENCE_PATTERN.search(text)
    if match:
        return match.group(1)
        
    isolated = re.search(r"\b(\d{9,20})\b", text)
    if isolated:
        val = isolated.group(1)
        if not re.match(r"^[\d.,]+$", val):
            return val
        return val
    return None


def _extract_merchant(text: str) -> Optional[str]:
    # Strip any occurrences of dates to prevent them appearing in the merchant string
    for pattern in DATE_PATTERNS:
        text = re.sub(pattern, "", text)

    hint = MERCHANT_HINT_PATTERN.search(text)
    if hint:
        return hint.group(1).strip(" .,-")

    cleaned = re.sub(r"\b(?:debit|dr|txn|transaction|ref|utr|id)\b", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^A-Za-z0-9 .&'-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,-")
    if len(cleaned) >= 3:
        return cleaned[:80]
    return None


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    from io import BytesIO

    from pypdf import PdfReader  # type: ignore[import-not-found]

    reader = PdfReader(BytesIO(file_bytes))
    chunks: List[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def extract_text_from_image_bytes(file_bytes: bytes) -> str:
    from io import BytesIO

    from PIL import Image

    image = Image.open(BytesIO(file_bytes))
    try:
        import pytesseract  # type: ignore[import-not-found]
    except Exception as exc:
        raise RuntimeError("Image OCR requires pytesseract and Tesseract OCR binary.") from exc

    tesseract_bin = shutil.which("tesseract")
    if tesseract_bin is None:
        windows_candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for candidate in windows_candidates:
            if Path(candidate).exists():
                pytesseract.pytesseract.tesseract_cmd = candidate
                tesseract_bin = candidate
                break

    if tesseract_bin is None:
        raise RuntimeError(
            "Tesseract OCR executable was not found in PATH. "
            "Install Tesseract and add it to PATH, or upload a PDF file instead."
        )

    # Force row-by-row extraction for tables instead of column-by-column
    return pytesseract.image_to_string(image, config='--psm 6 -c preserve_interword_spaces=1')


def detect_transactions(raw_text: str) -> List[ExtractedTransaction]:
    lines = _normalize_lines(raw_text)
    transactions = []
    current_tx = {"date": None, "merchant": [], "amounts": [], "ref_id": None, "lines": []}

    for line in lines:
        line_lower = line.lower()
        if _looks_like_credit(line_lower):
            continue
            
        # Ignore literal table header rows
        if "withdrawal" in line_lower and "balance" in line_lower:
            continue

        date_match: Optional[date] = None
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, line)
            if match:
                parsed = parse_date_safe(match.group(0))
                if parsed:
                    date_match = parsed
                    break

        amounts = _extract_amounts(line)
        ref_id = _extract_reference_id(line)

        if date_match and current_tx["date"] and current_tx["amounts"]:
            transactions.append(current_tx)
            current_tx = {"date": None, "merchant": [], "amounts": [], "ref_id": None, "lines": []}

        if date_match and not current_tx["date"]:
            current_tx["date"] = date_match

        if amounts:
            current_tx["amounts"].extend(amounts)

        if ref_id and not current_tx["ref_id"]:
            current_tx["ref_id"] = ref_id

        cleaned_text = re.sub(r"[\d/.-]", "", line).strip()
        if len(cleaned_text) > 3:
            current_tx["merchant"].append(line)

        current_tx["lines"].append(line)

    if current_tx["date"] and current_tx["amounts"]:
        transactions.append(current_tx)

    candidates: List[ExtractedTransaction] = []
    for tx in transactions:
        amount = tx["amounts"][0]
        full_text = " ".join(tx["merchant"])
        merchant = _extract_merchant(full_text) or "Card Transaction"
        
        candidates.append(
            ExtractedTransaction(
                amount=amount,
                transaction_date=tx["date"].isoformat(),
                merchant_name=merchant,
                transaction_type="debit",
                bank_reference_id=tx["ref_id"],
                source_line=" ".join(tx["lines"])[:200]
            )
        )

    if candidates:
        return _dedupe_candidates(candidates)

    fallback_date = _extract_first_date(raw_text) or date.today()
    amounts = _extract_amounts(raw_text)
    if not amounts:
        return []

    fallback = ExtractedTransaction(
        amount=amounts[0],
        transaction_date=fallback_date.isoformat(),
        merchant_name=_extract_merchant(raw_text) or "Bank Transaction",
        transaction_type="debit",
        bank_reference_id=_extract_reference_id(raw_text),
        source_line="inferred",
    )
    return [fallback]


def _dedupe_candidates(candidates: List[ExtractedTransaction]) -> List[ExtractedTransaction]:
    seen = set()
    output: List[ExtractedTransaction] = []
    for tx in candidates:
        key = (round(tx.amount, 2), tx.transaction_date, tx.merchant_name.lower(), tx.bank_reference_id or "")
        if key in seen:
            continue
        seen.add(key)
        output.append(tx)
    return output[:30]


def extract_transactions_from_file(file_bytes: bytes, suffix: str) -> ExtractionResult:
    lower_suffix = suffix.lower()
    if lower_suffix == ".pdf":
        text = extract_text_from_pdf_bytes(file_bytes)
    elif lower_suffix in {".jpg", ".jpeg", ".png"}:
        text = extract_text_from_image_bytes(file_bytes)
    else:
        raise ValueError("Unsupported file type")

    transactions = detect_transactions(text)
    return ExtractionResult(raw_text=text, transactions=transactions)


def safe_upload_name(original_filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", Path(original_filename).name)
    return cleaned[:120] or "upload"


def verify_file_signature(filename: str, content_type: Optional[str]) -> Tuple[bool, str]:
    suffix = Path(filename).suffix.lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    if suffix not in allowed:
        return False, "Unsupported file type"

    if content_type:
        allowed_mime = {
            "application/pdf",
            "image/jpeg",
            "image/jpg",
            "image/png",
            "application/octet-stream",
        }
        if content_type.lower() not in allowed_mime:
            return False, "Unsupported content type"

    return True, suffix
