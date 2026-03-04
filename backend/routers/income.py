from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from core.deps import get_current_user
from core.database import get_collection
from schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse, IncomeSummary
from models.helpers import income_helper

router = APIRouter(prefix="/income", tags=["Income"])


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    data: IncomeCreate,
    current_user: dict = Depends(get_current_user),
):
    incomes = get_collection("incomes")

    # Check if entry for this month + source already exists
    existing = await incomes.find_one({
        "user_id": current_user["_id"],
        "month": data.month,
        "source": data.source,
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Income entry for {data.month} with source '{data.source}' already exists. Use PUT to update."
        )

    new_income = {
        "user_id": current_user["_id"],
        "amount": data.amount,
        "source": data.source,
        "description": data.description,
        "month": data.month,
        "created_at": datetime.utcnow(),
    }
    result = await incomes.insert_one(new_income)
    new_income["_id"] = result.inserted_id
    return IncomeResponse(**income_helper(new_income))


@router.get("", response_model=List[IncomeResponse])
async def get_incomes(current_user: dict = Depends(get_current_user)):
    incomes = get_collection("incomes")
    cursor = incomes.find({"user_id": current_user["_id"]}).sort("month", -1)
    results = []
    async for inc in cursor:
        results.append(IncomeResponse(**income_helper(inc)))
    return results


@router.get("/summary", response_model=IncomeSummary)
async def get_income_summary(current_user: dict = Depends(get_current_user)):
    incomes = get_collection("incomes")
    cursor = incomes.find({"user_id": current_user["_id"]})

    all_incomes = []
    async for inc in cursor:
        all_incomes.append(inc)

    if not all_incomes:
        return IncomeSummary(
            total_income=0,
            average_monthly=0,
            income_count=0,
            by_month={},
            by_source={},
        )

    total = sum(i["amount"] for i in all_incomes)

    # Group by month
    by_month: dict = {}
    for i in all_incomes:
        m = i["month"]
        by_month[m] = by_month.get(m, 0) + i["amount"]

    avg = total / len(by_month) if by_month else 0

    # Group by source
    by_source: dict = {}
    for i in all_incomes:
        s = i.get("source", "Salary")
        by_source[s] = by_source.get(s, 0) + i["amount"]

    return IncomeSummary(
        total_income=round(total, 2),
        average_monthly=round(avg, 2),
        income_count=len(all_incomes),
        by_month={k: round(v, 2) for k, v in sorted(by_month.items())},
        by_source={k: round(v, 2) for k, v in by_source.items()},
    )


@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: str,
    data: IncomeUpdate,
    current_user: dict = Depends(get_current_user),
):
    incomes = get_collection("incomes")
    try:
        oid = ObjectId(income_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid income ID")

    income = await incomes.find_one({"_id": oid, "user_id": current_user["_id"]})
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    await incomes.update_one({"_id": oid}, {"$set": update_data})
    updated = await incomes.find_one({"_id": oid})
    return IncomeResponse(**income_helper(updated))


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: str,
    current_user: dict = Depends(get_current_user),
):
    incomes = get_collection("incomes")
    try:
        oid = ObjectId(income_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid income ID")

    result = await incomes.delete_one({"_id": oid, "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Income record not found")
