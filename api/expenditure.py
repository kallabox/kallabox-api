from fastapi import status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import api.models as models
import api.schemas as schemas
import api.oauth2 as oauth2
import api.functions as fun
from api.database import get_db
from uuid import uuid4

router = APIRouter(tags=["Expenditure"], prefix="/api")


@router.get(
    "/expenditure/view",
    response_model=List[schemas.ExpenditureOut],
    status_code=status.HTTP_200_OK,
)
def get_expenditure(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):
    """Get all expenditures"""
    if fun.verify_user_role(
        current_user.role, "user"
    ):  # User only gets to see his or her entries
        expenditures = (
            db.query(models.Expend)
            .filter(
                models.Expend.user_id == current_user.user_id,
                models.Expend.account_id == current_user.account_id,
            )
            .all()
        )

    if fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Account admin can see all the entries
        expenditures = (
            db.query(models.Expend)
            .filter(
                models.Expend.account_id == current_user.account_id,
            )
            .all()
        )

    if not expenditures:  # Expenditures pertaining to this account is not found
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Get Expenditure -> Expenditure not found",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expenditure for user with id: {current_user.user_id} is not found",
        )

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Get Expenditure -> Returning Requested Expenditures",
    )

    return expenditures


@router.post(
    "/expenditure/add",
    response_model=schemas.ExpenditureOut,
    status_code=status.HTTP_201_CREATED,
)
def create_expenditure(
    expend: schemas.ExpenditureCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Add expenditure to the database"""
    exp = fun.convert_to_valid_name(expend.expense)
    expense_type_object_query = db.query(models.ExpenseType).filter(
        models.ExpenseType.expense_type == exp,
        models.ExpenseType.account_id == current_user.account_id,
    )
    expense_type_object = (
        expense_type_object_query.first()
    )  # Getting the expense type object if it exists

    expense_dict = {"expense_type": exp}

    if (
        expense_type_object is None
    ):  # Creating a new one if expense type object does not exist and storing it in the database
        expense_type_id = uuid4()
        new_expense = models.ExpenseType(
            account_id=current_user.account_id,
            account_name=current_user.account_name,
            user_id=current_user.user_id,
            user_name=current_user.user_name,
            expense_type_id=expense_type_id,
            **expense_dict,
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

    else:
        expense_type_id = (
            expense_type_object.expense_type_id
        )  # Taking the expense type id from either the newly created one or the old one

    new_expend = models.Expend(
        account_id=current_user.account_id,
        account_name=current_user.account_name,
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        expend_id=uuid4(),
        amount=expend.amount,
        expense_type_id=expense_type_id,
    )
    db.add(new_expend)
    db.commit()
    db.refresh(new_expend)  # Adding the expenditure to the database

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Create Expenditure -> Returning Created Expenditure",
    )

    return new_expend


@router.put(
    "/expenditure/edit/",
    response_model=schemas.ExpenditureOut,
    status_code=status.HTTP_200_OK,
)  # id is expend_id
def update_expenditure(
    expenditure_update: schemas.ExpenditureUpdateIn,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    "Update the wrongly entered expenditure using expend_id as id and amount"
    expend_query = db.query(models.Expend).filter(
        models.Expend.expend_id == expenditure_update.expend_id
    )
    expend = expend_query.first()  # Checking for the expenditure object

    if expend is None:  # if expenditure object is not found for this user
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Update Expenditure -> Expenditure for this user does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expenditure with id: {expenditure_update.expend_id} does not exist",
        )
    if fun.verify_user_role(current_user.role, "user"):
        if (
            expend.user_id != current_user.user_id
            or current_user.account_id != expend.account_id
        ):
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="w",
                message="Update Expenditure -> User not permitted",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

    if fun.verify_user_role(current_user.role, "account_admin"):
        if expend.account_id != current_user.account_id:
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="w",
                message="Update Expenditure -> Not an Account Administrator",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

    exp = fun.convert_to_valid_name(expenditure_update.expense)
    expense_type = (
        db.query(models.ExpenseType)
        .filter(models.ExpenseType.expense_type == exp)
        .first()
    )  # Finding an existing one

    if (
        expense_type is None
    ):  # Creating a new expense type object and storing it in the database if it does not exist
        new_expense = models.ExpenseType(
            account_id=current_user.account_id,
            account_name=current_user.account_name,
            user_id=current_user.user_id,
            user_name=current_user.user_name,
            expense_type_id=uuid4(),
            expense_type=exp,
        )
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        expense_type_id = new_expense.expense_type_id

    else:
        expense_type_id = expense_type.expense_type_id

    updated_expenditure_dictionary = {
        "expense_type_id": expense_type_id,
        "amount": expenditure_update.amount,
    }
    expend_query.update(updated_expenditure_dictionary, synchronize_session=False)

    db.commit()  # Updating the expenditure
    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Update Expenditure -> Expenditure Updated",
    )

    return expend_query.first()
