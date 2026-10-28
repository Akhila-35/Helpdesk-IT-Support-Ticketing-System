from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_roles
)

from app.models.user import User
from app.schemas.auth import UserRead
from app.schemas.enums import UserRole


router = APIRouter()


# -----------------------------------------
# GET CURRENT LOGGED-IN USER
# -----------------------------------------

@router.get("/me", response_model=UserRead)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# -----------------------------------------
# GET ENGINEERS - ADMIN ONLY
# -----------------------------------------

@router.get("/engineers", response_model=list[UserRead])
def engineers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    engineers_list = (
        db.query(User)
        .filter(
            User.role == UserRole.ENGINEER,
            User.is_active.is_(True)
        )
        .all()
    )

    return engineers_list


# -----------------------------------------
# UPDATE USER ROLE - ADMIN ONLY
# -----------------------------------------

@router.post("/{user_id}/role", response_model=UserRead)
def role(
    user_id: int,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = role

    db.commit()
    db.refresh(user)

    return user