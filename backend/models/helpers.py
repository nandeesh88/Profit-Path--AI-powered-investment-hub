from bson import ObjectId
from datetime import datetime


def user_helper(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "monthly_income": user["monthly_income"],
        "risk_tolerance": user["risk_tolerance"],
        "financial_goal": user["financial_goal"],
        "age": user.get("age"),
        "created_at": user.get("created_at", datetime.utcnow()),
    }


def expense_helper(expense: dict) -> dict:
    return {
        "id": str(expense["_id"]),
        "user_id": str(expense["user_id"]),
        "description": expense["description"],
        "amount": expense["amount"],
        "category": expense["category"],
        "date": expense["date"],
        "transaction_type": expense.get("transaction_type", "debit"),
        "bank_reference_id": expense.get("bank_reference_id"),
        "source_document_id": str(expense.get("source_document_id")) if expense.get("source_document_id") else None,
        "created_at": expense.get("created_at", datetime.utcnow()),
    }


def income_helper(income: dict) -> dict:
    return {
        "id": str(income["_id"]),
        "user_id": str(income["user_id"]),
        "amount": income["amount"],
        "source": income.get("source", "Salary"),
        "description": income.get("description", ""),
        "month": income["month"],
        "created_at": income.get("created_at", datetime.utcnow()),
    }


def goal_helper(goal: dict) -> dict:
    target = goal["target_amount"]
    current = goal.get("current_amount", 0)
    progress = (current / target * 100) if target > 0 else 0
    return {
        "id": str(goal["_id"]),
        "user_id": str(goal["user_id"]),
        "title": goal["title"],
        "description": goal.get("description"),
        "target_amount": target,
        "current_amount": current,
        "progress_percentage": round(min(progress, 100), 2),
        "target_date": goal["target_date"],
        "category": goal.get("category", "Other"),
        "priority": goal.get("priority", "medium"),
        "created_at": goal.get("created_at", datetime.utcnow()),
    }
