from fastapi import APIRouter, Depends, HTTPException, status
from core.deps import get_current_user
from schemas.user import UserResponse, UserUpdate
from models.helpers import user_helper
from core.database import get_collection
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**user_helper(current_user))


@router.put("/me", response_model=UserResponse)
async def update_me(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    users = get_collection("users")
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    await users.update_one(
        {"_id": ObjectId(str(current_user["_id"]))},
        {"$set": update_data},
    )
    updated = await users.find_one({"_id": current_user["_id"]})
    return UserResponse(**user_helper(updated))
