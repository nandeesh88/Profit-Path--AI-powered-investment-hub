from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, date
from bson import ObjectId
from calendar import monthrange

from core.deps import get_current_user
from core.database import get_collection
from schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummary
from models.helpers import expense_helper

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    current_user: dict = Depends(get_current_user),
):
    expenses = get_collection("expenses")
    new_expense = {
        "user_id": current_user["_id"],
        "description": data.description,
        "amount": data.amount,
        "category": data.category,
        "date": data.date.isoformat(),
        "created_at": datetime.utcnow(),
    }
    result = await expenses.insert_one(new_expense)
    new_expense["_id"] = result.inserted_id
    new_expense["date"] = data.date
    return ExpenseResponse(**expense_helper(new_expense))


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
