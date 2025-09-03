from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import LoginAuthentication
from schemas import LoginRequest

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user in DB
    user = (
        db.query(LoginAuthentication)
        .filter(
            LoginAuthentication.username == request.username,
            LoginAuthentication.password == request.password,   # ⚠️ Plain-text just for demo!
            LoginAuthentication.role == request.role,
            LoginAuthentication.isactive == True,
            LoginAuthentication.isdelete == False
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return {"message": "Login successful"}
