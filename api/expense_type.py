from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import api.models as models
import api.schemas as schemas
import api.oauth2 as oauth2
import api.functions as fun
from api.database import get_db
from uuid import uuid4

router = APIRouter(tags=["Expense Type"], prefix="/api")


@router.get("/expense/view", response_model=List[schemas.ExpenseTypeOut])
def get_expense_type(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    """Get all the expense types from the database"""

    if fun.verify_user_role(
        current_user.role, "user"
    ):  # Verifying whether the current token bearer is a user and not an account_admin. Token bearer will be returned expense types pertaining to the ones added by the bearer.
        expense_types = (
            db.query(models.ExpenseType)
            .filter(
                models.ExpenseType.user_id == current_user.user_id,
                models.ExpenseType.account_id == current_user.account_id,
            )
            .all()
        )

    if fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Verifying whether the current token bearer is an account_admin and will be returned expense types pertaining to that account.
        expense_types = (
            db.query(models.ExpenseType)
            .filter(
                models.ExpenseType.account_id == current_user.account_id,
            )
            .all()
        )

    if not expense_types:  # Raising an error if expense types is not found
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Get Expense Type -> Expense Type for this user does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense Type for user with id: {current_user.user_id} not found",
        )

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Get Expense Type -> Requested Expense Types Returned",
    )

    return expense_types  # Returning all the expense types


@router.post(
    "/expense/add",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ExpenseTypeOut,
)
def add_expense_type(
    expense: schemas.ExpenseTypeIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add an expense type to the database"""

    exp = fun.convert_to_valid_name(
        expense.expense_type
    )  # Converting the expense types entered by the user to all uppercase letters with no spaces
    expense.expense_type = exp

    expense_type = (
        db.query(models.ExpenseType)
        .filter(
            models.ExpenseType.account_id == current_user.account_id,
            models.ExpenseType.expense_type == exp,
        )
        .first()
    )  # Checking whether the same expense type exists for this account

    if (
        expense_type is not None
    ):  # If exists then raising an error indicating that an entry already exists for this account in the database.
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Add Expense Type -> Expense type for this user already exists",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Expense Type already exists",
        )

    new_expense = models.ExpenseType(
        account_id=current_user.account_id,
        account_name=current_user.account_name,
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        expense_type_id=uuid4(),
        **expense.dict(),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)  # Creating and adding a new expense type

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Add Expense Type -> Expense Type added",
    )

    return new_expense  # Returning the newly created expense type


@router.put(
    "/expense/edit/", response_model=schemas.ExpenseTypeOut
)  # Endpoint for when edit button is triggered
def update_expense_type(
    expense_update: schemas.ExpenseTypeUpdateIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Update a wrongly entered expense type in the database using the transaction id as id and expense type"""

    expense_type_query = db.query(models.ExpenseType).filter(
        models.ExpenseType.expense_type_id == expense_update.expense_type_id
    )
    expense_type = expense_type_query.first()  # Getting the expense type query

    exp = fun.convert_to_valid_name(expense_update.expense_type)
    expense_update.expense_type = exp

    if expense_type is None:  # If expense type does not exist
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Update Expense Type -> Expense Type for this user does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense Type with id: {expense_update.expense_type_id} does not exist",
        )
    if fun.verify_user_role(
        current_user.role, "user"
    ):  # Refraining an user from updating expense types
        if (
            expense_type.user_id != current_user.user_id
            or expense_type.account_id != current_user.account_id
        ):
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="w",
                message="Update Expense Type -> User not permitted to perform requested action",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the requested action",
            )

    if fun.verify_user_role(current_user.role, "account_admin"):
        if (
            expense_type.account_id != current_user.account_id
        ):  # Preventing an Account Administrator from changing other accounts' expense types
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="c",
                message="Update Expense Type -> Account Administrator trying to alter the entries of another account",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the requested action",
            )

    update_expense_dict = {
        "expense_type_id": expense_update.expense_type_id,
        "expense_type": exp,
    }
    expense_type_query.update(update_expense_dict, synchronize_session=False)
    db.commit()  # Updating the expense type

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Update Expense Type -> Expense Type Updated",
    )
    return expense_type_query.first()
