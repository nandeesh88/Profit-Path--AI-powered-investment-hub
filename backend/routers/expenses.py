from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List, Optional
from datetime import datetime, date
from bson import ObjectId
from pathlib import Path
import logging
import re

from core.deps import get_current_user
from core.database import get_collection
from core.transaction_extractor import (
    extract_transactions_from_file,
    safe_upload_name,
    sha256_bytes,
    verify_file_signature,
)
from schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseSummary,
    ExpenseExtractionResponse,
    ExpenseFromExtractionCreate,
    ExtractedTransaction,
)
from models.helpers import expense_helper

router = APIRouter(prefix="/expenses", tags=["Expenses"])
logger = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "secure_uploads"


async def _is_duplicate_expense(
    user_id: ObjectId,
    amount: float,
    tx_date: date,
    description: str,
    bank_reference_id: Optional[str] = None,
) -> bool:
    expenses = get_collection("expenses")
    if bank_reference_id:
        by_ref = await expenses.find_one(
            {
                "user_id": user_id,
                "bank_reference_id": bank_reference_id,
            }
        )
        if by_ref:
            return True

    escaped_description = re.escape(description.strip())
    desc_regex = {"$regex": f"^{escaped_description}$", "$options": "i"}
    duplicate = await expenses.find_one(
        {
            "user_id": user_id,
            "date": tx_date.isoformat(),
            "amount": {"$gte": round(amount - 0.01, 2), "$lte": round(amount + 0.01, 2)},
            "description": desc_regex,
        }
    )
    return duplicate is not None


async def _create_expense_doc(
    *,
    current_user: dict,
    description: str,
    amount: float,
    category: str,
    tx_date: date,
    transaction_type: str = "debit",
    bank_reference_id: Optional[str] = None,
    source_document_id: Optional[str] = None,
) -> ExpenseResponse:
    if transaction_type != "debit":
        raise HTTPException(status_code=400, detail="Only debit transactions can be added as expenses")

    if await _is_duplicate_expense(
        user_id=current_user["_id"],
        amount=amount,
        tx_date=tx_date,
        description=description,
        bank_reference_id=bank_reference_id,
    ):
        raise HTTPException(status_code=409, detail="Duplicate transaction detected")

    source_doc_oid: Optional[ObjectId] = None
    if source_document_id:
        try:
            source_doc_oid = ObjectId(source_document_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid source document ID")

    expenses = get_collection("expenses")
    new_expense = {
        "user_id": current_user["_id"],
        "description": description,
        "amount": amount,
        "category": category,
        "date": tx_date.isoformat(),
        "transaction_type": "debit",
        "bank_reference_id": bank_reference_id,
        "source_document_id": source_doc_oid,
        "created_at": datetime.utcnow(),
    }
    result = await expenses.insert_one(new_expense)
    new_expense["_id"] = result.inserted_id
    new_expense["date"] = tx_date

    if source_document_id:
        expense_documents = get_collection("expense_documents")
        await expense_documents.update_one(
            {"_id": source_doc_oid, "user_id": current_user["_id"]},
            {"$addToSet": {"linked_expense_ids": result.inserted_id}},
        )

    return ExpenseResponse(**expense_helper(new_expense))


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: dict = Depends(get_current_user),
):
    return await _create_expense_doc(
        current_user=current_user,
        description=data.description,
        amount=data.amount,
        category=data.category,
        tx_date=data.date,
        transaction_type=data.transaction_type,
        bank_reference_id=data.bank_reference_id,
        source_document_id=data.source_document_id,
    )


@router.post("/upload-extract", response_model=ExpenseExtractionResponse)
async def upload_and_extract_transactions(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    is_valid, signature = verify_file_signature(file.filename or "", file.content_type)
    if not is_valid:
        raise HTTPException(status_code=400, detail=signature)

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 10MB limit")

    try:
        extraction = extract_transactions_from_file(file_bytes, signature)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to extract transaction details: {exc}") from exc

    if not extraction.transactions:
        raise HTTPException(status_code=400, detail="No debit transactions detected in uploaded document")

    user_folder = UPLOAD_ROOT / str(current_user["_id"])
    user_folder.mkdir(parents=True, exist_ok=True)

    upload_id = ObjectId()
    safe_name = safe_upload_name(file.filename or "document")
    stored_name = f"{upload_id}_{safe_name}"
    stored_path = user_folder / stored_name
    try:
        stored_path.write_bytes(file_bytes)
    except Exception as exc:
        logger.exception("Failed to persist uploaded expense document")
        raise HTTPException(status_code=500, detail="Failed to store uploaded file") from exc

    sha256 = sha256_bytes(file_bytes)
    expense_documents = get_collection("expense_documents")
    try:
        await expense_documents.insert_one(
            {
                "_id": upload_id,
                "user_id": current_user["_id"],
                "original_filename": file.filename,
                "stored_filename": stored_name,
                "stored_path": str(stored_path),
                "content_type": file.content_type,
                "sha256": sha256,
                "size_bytes": len(file_bytes),
                "raw_text": extraction.raw_text[:10000],
                "linked_expense_ids": [],
                "created_at": datetime.utcnow(),
            }
        )
    except Exception as exc:
        logger.exception("Failed to store expense document metadata")
        raise HTTPException(status_code=500, detail="Failed to store upload metadata") from exc

    tx_payload: List[ExtractedTransaction] = []
    for tx in extraction.transactions:
        try:
            duplicate = await _is_duplicate_expense(
                user_id=current_user["_id"],
                amount=tx.amount,
                tx_date=date.fromisoformat(tx.transaction_date),
                description=tx.merchant_name,
                bank_reference_id=tx.bank_reference_id,
            )
        except Exception:
            logger.exception("Duplicate check failed for extracted transaction")
            duplicate = False
        tx_payload.append(
            ExtractedTransaction(
                amount=round(tx.amount, 2),
                transaction_date=date.fromisoformat(tx.transaction_date),
                merchant_name=tx.merchant_name,
                transaction_type="debit",
                bank_reference_id=tx.bank_reference_id,
                is_duplicate=duplicate,
            )
        )

    return ExpenseExtractionResponse(
        upload_id=str(upload_id),
        filename=file.filename or safe_name,
        transactions=tx_payload,
    )


@router.post("/from-extraction", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_from_extraction(
    data: ExpenseFromExtractionCreate,
    current_user: dict = Depends(get_current_user),
):
    expense_documents = get_collection("expense_documents")
    try:
        upload_oid = ObjectId(data.upload_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid upload ID")

    upload_doc = await expense_documents.find_one({"_id": upload_oid, "user_id": current_user["_id"]})
    if not upload_doc:
        raise HTTPException(status_code=404, detail="Uploaded document not found")

    return await _create_expense_doc(
        current_user=current_user,
        description=data.description,
        amount=data.amount,
        category=data.category,
        tx_date=data.date,
        transaction_type=data.transaction_type,
        bank_reference_id=data.bank_reference_id,
        source_document_id=data.upload_id,
    )


@router.get("", response_model=List[ExpenseResponse])
async def get_expenses(current_user: dict = Depends(get_current_user)):
    expenses = get_collection("expenses")
    cursor = expenses.find({"user_id": current_user["_id"]}).sort("date", -1)
    results = []
    async for exp in cursor:
        # Normalize date field
        if isinstance(exp["date"], str):
            exp["date"] = date.fromisoformat(exp["date"])
        results.append(ExpenseResponse(**expense_helper(exp)))
    return results


@router.get("/summary", response_model=ExpenseSummary)
async def get_expense_summary(current_user: dict = Depends(get_current_user)):
    expenses = get_collection("expenses")
    cursor = expenses.find({"user_id": current_user["_id"]})

    all_expenses = []
    async for exp in cursor:
        if isinstance(exp["date"], str):
            exp["date"] = date.fromisoformat(exp["date"])
        all_expenses.append(exp)

    if not all_expenses:
        return ExpenseSummary(
            total_expenses=0,
            monthly_expenses=0,
            average_expense=0,
            expense_count=0,
            by_category={},
        )

    total = sum(e["amount"] for e in all_expenses)
    avg = total / len(all_expenses)

    # Monthly: current month
    today = date.today()
    monthly = sum(
        e["amount"]
        for e in all_expenses
        if isinstance(e["date"], date) and e["date"].month == today.month and e["date"].year == today.year
    )

    by_cat: dict = {}
    for e in all_expenses:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]

    return ExpenseSummary(
        total_expenses=round(total, 2),
        monthly_expenses=round(monthly, 2),
        average_expense=round(avg, 2),
        expense_count=len(all_expenses),
        by_category={k: round(v, 2) for k, v in by_cat.items()},
    )


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    current_user: dict = Depends(get_current_user),
):
    expenses = get_collection("expenses")
    try:
        oid = ObjectId(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid expense ID")

    expense = await expenses.find_one({"_id": oid, "user_id": current_user["_id"]})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "date" in update_data:
        update_data["date"] = update_data["date"].isoformat()
    if "transaction_type" in update_data and update_data["transaction_type"] != "debit":
        raise HTTPException(status_code=400, detail="Only debit transactions are allowed")

    candidate_description = update_data.get("description", expense["description"])
    candidate_amount = update_data.get("amount", expense["amount"])
    candidate_date_str = update_data.get("date", expense["date"])
    candidate_date = date.fromisoformat(candidate_date_str) if isinstance(candidate_date_str, str) else candidate_date_str
    original_date = date.fromisoformat(expense["date"]) if isinstance(expense["date"], str) else expense["date"]
    candidate_ref = update_data.get("bank_reference_id", expense.get("bank_reference_id"))

    duplicate = await _is_duplicate_expense(
        user_id=current_user["_id"],
        amount=float(candidate_amount),
        tx_date=candidate_date,
        description=candidate_description,
        bank_reference_id=candidate_ref,
    )
    if duplicate and (
        candidate_description.lower() != expense["description"].lower()
        or round(float(candidate_amount), 2) != round(float(expense["amount"]), 2)
        or candidate_date.isoformat() != original_date.isoformat()
    ):
        raise HTTPException(status_code=409, detail="Duplicate transaction detected")

    await expenses.update_one({"_id": oid}, {"$set": update_data})
    updated = await expenses.find_one({"_id": oid})
    if isinstance(updated["date"], str):
        updated["date"] = date.fromisoformat(updated["date"])
    return ExpenseResponse(**expense_helper(updated))


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user),
):
    expenses = get_collection("expenses")
    try:
        oid = ObjectId(expense_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid expense ID")

    result = await expenses.delete_one({"_id": oid, "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
