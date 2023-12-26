from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import api.models as models
import api.schemas as schemas
import api.oauth2 as oauth2
import api.functions as fun
from api.database import get_db
from uuid import uuid4

router = APIRouter(tags=["Income"], prefix="/api")


@router.get(
    "/income/view",
    response_model=List[schemas.IncomeOut],
    status_code=status.HTTP_200_OK,
)
def get_income(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    """Get all incomes."""

    if fun.verify_user_role(
        current_user.role, "user"
    ):  # Getting the incomes pertaining to the user
        incomes = (
            db.query(models.Income)
            .filter(
                func.date(models.Income.timestamp) == date.today(),
                models.Income.user_id == current_user.user_id,
                models.Income.account_id == current_user.account_id,
            )
            .all()
        )

    if fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Getting the incomes pertaining to the account admin
        incomes = (
            db.query(models.Income)
            .filter(
                func.date(models.Income.timestamp) == date.today(),
                models.Income.account_id == current_user.account_id,
            )
            .all()
        )

    if not incomes:  # If no income is found for this user or account administrator
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Get Income -> Income for this user does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income for user with id: {current_user.user_id} is not found",
        )

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Get Income -> Requested Incomes Returned",
    )

    return incomes


@router.post(
    "/income/add", status_code=status.HTTP_201_CREATED, response_model=schemas.IncomeOut
)
def add_income(
    income: schemas.IncomeIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add income to the database"""
    new_income = models.Income(
        account_id=current_user.account_id,
        account_name=current_user.account_name,
        trans_id=uuid4(),
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        **income.dict(),
    )
    db.add(new_income)
    db.commit()
    db.refresh(new_income)  # Adding the new income model to the database

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Add Income -> Income added",
    )
    return new_income


@router.put(
    "/income/edit/",
    response_model=schemas.IncomeOut,
    status_code=status.HTTP_200_OK,
)  # Endpoint for when edit button is triggered
def update_income(
    income_update: schemas.IncomeUpdateIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Update a wrongly entered income in the database using the transaction id as id and amount"""

    income_query = db.query(models.Income).filter(
        models.Income.trans_id == income_update.trans_id
    )
    income = (
        income_query.first()
    )  # Getting the income query corresponding to the transaction id

    if income is None:  # If no income is found
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Update Income -> Requested Income does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income with id: {income_update.trans_id} does not exist",
        )
    if fun.verify_user_role(
        current_user.role, "user"
    ):  # Refraining user from altering other users' incomes
        if (
            income.user_id != current_user.user_id
            or income.account_id != current_user.account_id
        ):
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="c",
                message="Update Income -> User does not have privileges to update others' incomes",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the requested action",
            )

    if fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Refraining account administrator from altering other accounts' incomes
        if income.account_id != current_user.account_id:
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="c",
                message="Update Income -> Account Administrator trying to change the entries of other account",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the requested action",
            )

    income_update_dict = {
        "amount": income_update.amount,
    }

    income_query.update(income_update_dict, synchronize_session=False)
    db.commit()  # Updating the incomes table

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Update Income -> Requested Income Updated",
    )
    return income_query.first()
