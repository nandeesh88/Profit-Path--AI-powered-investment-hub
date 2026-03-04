from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, date
from bson import ObjectId

from core.deps import get_current_user
from core.database import get_collection
from schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from models.helpers import goal_helper

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(data: GoalCreate, current_user: dict = Depends(get_current_user)):
    goals = get_collection("goals")
    new_goal = {
        "user_id": current_user["_id"],
        "title": data.title,
        "description": data.description,
        "target_amount": data.target_amount,
        "current_amount": data.current_amount,
        "target_date": data.target_date.isoformat(),
        "category": data.category,
        "priority": data.priority or "medium",
        "created_at": datetime.utcnow(),
    }
    result = await goals.insert_one(new_goal)
    new_goal["_id"] = result.inserted_id
    new_goal["target_date"] = data.target_date
    return GoalResponse(**goal_helper(new_goal))


@router.get("", response_model=List[GoalResponse])
async def get_goals(current_user: dict = Depends(get_current_user)):
    goals = get_collection("goals")
    cursor = goals.find({"user_id": current_user["_id"]}).sort("created_at", -1)
    results = []
    async for g in cursor:
        if isinstance(g["target_date"], str):
            g["target_date"] = date.fromisoformat(g["target_date"])
        results.append(GoalResponse(**goal_helper(g)))
    return results


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    data: GoalUpdate,
    current_user: dict = Depends(get_current_user),
):
    goals = get_collection("goals")
    try:
        oid = ObjectId(goal_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid goal ID")

    goal = await goals.find_one({"_id": oid, "user_id": current_user["_id"]})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if "target_date" in update_data:
        update_data["target_date"] = update_data["target_date"].isoformat()

    await goals.update_one({"_id": oid}, {"$set": update_data})
    updated = await goals.find_one({"_id": oid})
    if isinstance(updated["target_date"], str):
        updated["target_date"] = date.fromisoformat(updated["target_date"])
    return GoalResponse(**goal_helper(updated))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    goals = get_collection("goals")
    try:
        oid = ObjectId(goal_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid goal ID")

    result = await goals.delete_one({"_id": oid, "user_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
