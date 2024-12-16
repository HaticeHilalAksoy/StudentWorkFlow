from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.models.user import UserLogin

router = APIRouter()

@router.post("/login")
def login_user(user: UserLogin):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE email = %s AND password = %s",
            (user.email, user.password)
        )
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"message": "Login successful", "user": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
