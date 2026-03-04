from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from bson import ObjectId

from core.database import get_collection
from core.security import hash_password, verify_password, create_access_token
from schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from models.helpers import user_helper

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    users = get_collection("users")

    # Check duplicate email
    existing = await users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "monthly_income": user_data.monthly_income,
        "risk_tolerance": user_data.risk_tolerance,
        "financial_goal": user_data.financial_goal,
        "created_at": datetime.utcnow(),
    }
    result = await users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse(**user_helper(new_user)),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    users = get_collection("users")
    user = await users.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(
        access_token=token,
        user=UserResponse(**user_helper(user)),
    )
