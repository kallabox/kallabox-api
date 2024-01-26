from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import api.database as database
import api.schemas as schemas
import api.models as models
import api.utils as utils
import api.functions as fun
import api.oauth2 as oauth2
from sqlalchemy.exc import IntegrityError
from uuid import uuid4


router = APIRouter(tags=["Account"], prefix="/api")


@router.get(
    "/account/admin/users/view", response_model=List[schemas.AccountUserOut]
)  # For account_admin
def get_users(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Get current users in the account"""
    if fun.verify_user_role(
        current_user.role, "user"
    ):  # To verify if the token bearer is an account_admin
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Get Users -> Not an Account Administrator",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    users = (
        db.query(models.User)
        .filter(models.User.account_id == current_user.account_id)
        .all()
    )  # Finding all the users in this account

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Get Users -> Users Returned",
    )

    return users


@router.put("/account/admin/user/role", response_model=schemas.AccountUserUpdateOut)
def update_user_role(
    user_account_name: schemas.AccountUserUpdateIn,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Update the role of an user in an account by account_admin"""

    if not fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Verify if the current token bearer is an account_admin
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Update User Role -> Not an Account Administrator",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    if fun.verify_user_role(user_account_name.role, "user") and str(
        user_account_name.user_name
    ) == str(
        current_user.user_name
    ):  # Verify if the there are other account_admins before changing the role of the current token bearer who is an account_admin
        check_admin = db.query(
            models.User.account_id == current_user.account_id,
            models.User.user_id != current_user.user_id,
            models.User.role == "account_admin",
        ).first()

        if (
            check_admin is None
        ):  # Not allow if the current token bearer is the only account_admin for this account
            fun.logger(
                account_id=str(current_user.account_id),
                user_id=str(current_user.user_id),
                log_type="w",
                message="Update User Role -> Changing role of the only administrator is not permitted",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
            )

    user_query = db.query(models.User).filter(
        models.User.account_id == current_user.account_id,
        models.User.user_name == user_account_name.user_name,
    )  # Finding the user to change the role within the account
    user = user_query.first()

    if user is None:  # Raising an error if the user is not found within this account
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Update User Role -> User does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    user_role = {"role": user_account_name.role}

    user_query.update(user_role, synchronize_session=False)  # Updating the role
    db.commit()  # Committing to the changes

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Update User Role -> Requested User Role Updated",
    )

    return user_query.first()  # Returning the updated user details


@router.post(
    "/account/create/user",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
)
def add_user(
    user_cred: schemas.UserCredentials,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Create the user for the account and add in database"""

    if not fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Verification if the current token bearer is an account_admin
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Add User -> Not an Account Administrator",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    hashed_password = utils.hash(user_cred.password)
    user_cred.password = (
        hashed_password  # Changing the original password to a hashed one
    )

    if (
        not user_cred.phone.isdigit()
    ):  # Check whether the phone numbers contain only integers
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="e",
            message="Add User -> Phone number does not contain integers",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone number must contain only integers",
        )

    user_cred.phone = str(user_cred.phone)

    account = (
        db.query(models.Account)
        .filter(models.Account.account_id == current_user.account_id)
        .first()
    )  # Finding the account

    acne_cat = account.account_name + "---" + user_cred.email

    try:
        new_user = models.User(
            user_id=uuid4(),
            acne=acne_cat,
            account_id=account.account_id,
            account_name=account.account_name,
            user_name=user_cred.user_name,
            email=user_cred.email,
            phone=user_cred.phone,
            password=hashed_password,
            role=user_cred.role,
        )  # Creating a new new_user

        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # Committing the changes

    except (
        IntegrityError
    ):  # If user with email or username is already present, rollback the previous commitment and raise an error
        db.rollback()
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Add User -> User trying to add already exists",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email or username in this account already exists",
        )

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Add User -> Requested User Added",
    )

    return new_user


@router.delete("/account/remove/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_detail: schemas.AccountUserDeleteIn,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Delete the user from account"""

    if not fun.verify_user_role(
        current_user.role, "account_admin"
    ):  # Verify if the current token bearer is an account admin
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Delete User -> Not an account administator",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    user_query = db.query(models.User).filter(
        models.User.account_id == current_user.account_id,
        models.User.user_name == user_detail.user_name,
    )
    user = user_query.first()  # Finding the user

    if user is None:  # If user not found then raise error
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Delete User -> User trying to delete does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    # Deleting all the entries in the income, expenditure, expense type and tokens table

    income_query = db.query(models.Income).filter(models.Income.user_id == user.user_id)

    expenditure_query = db.query(models.Expend).filter(
        models.Expend.user_id == user.user_id
    )

    expense_query = db.query(models.ExpenseType).filter(
        models.ExpenseType.user_id == user.user_id
    )

    token_query = db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user.user_id
    )

    if income_query.all() is not None:
        income_query.delete(synchronize_session=False)
        db.commit()

    if expenditure_query.all() is not None:
        expenditure_query.delete(synchronize_session=False)
        db.commit()

    if expense_query.all() is not None:
        expense_query.delete(synchronize_session=False)
        db.commit()

    if token_query.all() is not None:
        token_query.delete(synchronize_session=False)
        db.commit()

    # Finally deleting the user from the user's table

    user_query.delete(synchronize_session=False)
    db.commit()  # Delete the user

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Delete User -> Requested User Deleted",
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )  # Returning status code 204 after successful deletion
