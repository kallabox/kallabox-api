from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
import api.database as database
import api.schemas as schemas
import api.models as models
import api.utils as utils
import api.oauth2 as oauth2
import api.functions as fun
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

router = APIRouter(tags=["Super Admin"], prefix="/api")


@router.put(
    "/admin/account/user",
    response_model=schemas.AccountUserUpdateOut,
    status_code=status.HTTP_200_OK,
)
def update_user_role(
    user_update: schemas.SuperAdminUserUpdateIn,
    db: Session = Depends(database.get_db),
    signup_key=Depends(oauth2.check_signup_key),
):
    """Update the user's role using account name and email"""
    signup_key  # checking the validity of signup key
    account = (
        db.query(models.Account)
        .filter(models.Account.account_name == user_update.account_name)
        .first()
    )  # Searching for the account
    user_query = db.query(models.User).filter(
        models.User.account_id == account.account_id,
        models.User.user_name == user_update.user_name,
    )
    user = user_query.first()  # Searching for the user

    if user is None:  # Raise an error if the user is not found
        fun.logger_sa(log_type="w", message="Update User Role -> User does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    role_change = {"role": user_update.role}

    user_query.update(
        role_change, synchronize_session=False
    )  # Updating the user's role
    db.commit()  # Commiting the changes

    fun.logger_sa(
        log_type="i", message="Update User Role -> Requested User Role updated"
    )

    return user_query.first()  # Returning the updated user


@router.delete("/admin/account", status_code=status.HTTP_204_NO_CONTENT)
def purge_account(
    account_cred: schemas.SuperAdminAccountDelete,
    db: Session = Depends(database.get_db),
    signup_key=Depends(oauth2.check_signup_key),
):
    """Delete the account from the accounts table and all the users in that account in the users table"""
    signup_key
    account_query = db.query(models.Account).filter(
        models.Account.account_name == account_cred.account_name
    )
    account = account_query.first()  # Searching for the account

    if account is None:  # Raise an error if account is not found
        fun.logger_sa(log_type="w", message="Purge Account -> Account does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account does not exist",
        )

    income_query = db.query(models.Income).filter(
        models.Income.account_id == account.account_id
    )
    expenditure_query = db.query(models.Expend).filter(
        models.Expend.account_id == account.account_id
    )
    expense_type_query = db.query(models.ExpenseType).filter(
        models.ExpenseType.account_id == account.account_id
    )

    tokens_table_query = db.query(models.RefreshToken).filter(
        models.RefreshToken.account_id == account.account_id
    )

    if (
        income_query.all() is not None
    ):  # Delete all the entries in the income table pertaining to this account
        income_query.delete(synchronize_session=False)
        db.commit()

    if (
        expenditure_query.all() is not None
    ):  # Delete all the entries in the expenditure table pertaining to this account
        expenditure_query.delete(synchronize_session=False)
        db.commit()

    if (
        expense_type_query.all() is not None
    ):  # Delete all the entries in the expense type table pertaining to this account
        expense_type_query.delete(synchronize_session=False)
        db.commit()

    if tokens_table_query.all() is not None:
        # Delete all the entries in the tokens table pertaining to this account
        tokens_table_query.delete(synchronize_session=False)
        db.commit()

    users_query = db.query(models.User).filter(
        models.User.account_id == account.account_id
    )
    users = users_query.all()  # Searching for all users within the account

    if users is None:  # Raise an error if no user is found
        fun.logger_sa(log_type="w", message="Purge Account -> User does not exist")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users for the account does not exist",
        )

    users_query.delete(
        synchronize_session=False
    )  # Delete all the users from the users table
    db.commit()

    account_query.delete(synchronize_session=False)
    db.commit()  # Finally deleting the account itself

    fun.logger_sa(log_type="i", message="Purge Account -> Account purged")

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )  # Returning status code 204 after successful deletion


@router.delete("/admin/account/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_cred: schemas.SuperAdminUserDelete,
    db: Session = Depends(database.get_db),
    signup_key=Depends(oauth2.check_signup_key),
):
    """Delete the user associated with account from the users table"""
    signup_key  # Checking the signup key

    user_query = db.query(models.User).filter(
        models.User.account_name == user_cred.account_name,
        models.User.user_name == user_cred.user_name,
    )
    user = user_query.first()  # Searching for the user

    if user is None:  # Raise an error if user is not found
        fun.logger_sa(
            log_type="w", message="Delete User -> Requested User does not exist"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User for the account does not exist",
        )

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

    user_query.delete(synchronize_session=False)
    db.commit()  # Delete the user

    fun.logger_sa(log_type="i", message="Delete User -> Requested User deleted")

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )  # Returning status code 204 after successful deletion


@router.post("/admin/account/create", response_model=schemas.AccountOut)
def create_account(
    account_credentials: schemas.AccountIn,
    db: Session = Depends(database.get_db),
    signup_key=Depends(oauth2.check_signup_key),
):
    """Creates an account using the account name and the first user creating the account will be the default account_admin for that account"""

    signup_key  # Checking the validity of signup_key
    fun.check_account_name(
        account_credentials.account_name
    )  # Check if the account name is lowercase alphanumeric characters with no spaces
    account = models.Account(
        account_id=uuid4(), account_name=account_credentials.account_name
    )

    acne_cat = account_credentials.account_name + "---" + account_credentials.email

    password = account_credentials.password
    hashed_password = utils.hash(password)  # Hashing the password of account_admin

    if (
        not account_credentials.phone.isdigit()
    ):  # Checking if phone number only contains integers
        fun.logger_sa(
            log_type="c",
            message="Create Account -> Phone number must contain only integers of size 10",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Phone number must only contain integers",
        )

    account_credentials.phone = str(account_credentials.phone)

    user = (
        db.query(models.User)
        .filter(models.User.user_name == account_credentials.user_name)
        .all()
    )

    if (
        len(user) != 0
    ):  # Raise an error if the user is already present with the same username
        fun.logger_sa(
            log_type="w", message="Create Account -> Requested User Name already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Name already exists"
        )

    account_admin = models.User(
        account_id=account.account_id,
        account_name=account_credentials.account_name,
        user_id=uuid4(),
        user_name=account_credentials.user_name,
        email=account_credentials.email,
        phone=account_credentials.phone,
        password=hashed_password,
        role="account_admin",
        acne=acne_cat,
    )
    try:  # Try creating an account
        db.add(account)
        db.commit()
        db.refresh(account)

    except (
        IntegrityError
    ):  # Rollback the previous addition to the accounts database if account name already exists
        db.rollback()
        fun.logger_sa(
            log_type="w", message="Create Account -> Requested Account already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )

    user = (
        db.query(models.User)
        .filter(
            models.User.account_id == account_admin.account_id,
            models.User.user_id == account_admin.user_id,
            models.User.email == account_admin.email,
            models.User.user_name == account_admin.user_name,
        )
        .all()
    )

    if len(user) != 0:
        fun.logger_sa(
            log_type="w", message="Create Account -> Requested User already exists"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email or username in this account already exists",
        )

    else:
        db.add(account_admin)
        db.commit()
        db.refresh(account_admin)

    fun.logger_sa(log_type="i", message="Create Account -> Requested Account Created")

    return account_admin  # Returning the account_admin details (which also contains the account name and id)


@router.delete("/admin/account/", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    user_cred: schemas.SuperAdminAccountDelete,
    db: Session = Depends(database.get_db),
    signup_key=Depends(oauth2.check_signup_key),
):
    """Soft Delete the account by marking the status of the account as False"""
    signup_key

    account_query = db.query(models.Account).filter(
        models.Account.account_name == user_cred.account_name
    )
    account = account_query.first()  # Searching for the account

    if account is None:  # Raising an error if account is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account does not exist",
        )
    account_status = {"status": False}
    account_query.update(account_status, synchronize_session=False)
    db.commit()  # Changing the status of account to False and commiting the changes

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )  # Returning status code 204 after successfully soft deleting the account


@router.get(
    "/admin/income",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.IncomeOut],
)
def get_income(
    db: Session = Depends(database.get_db), signup_key=Depends(oauth2.check_signup_key)
):
    """Gets incomes associated with all the accounts and users"""

    signup_key  # Checking signup key

    incomes = db.query(models.Income).all()  # Getting all the incomes

    if not incomes:  # Raising an error if incomes is not found
        fun.logger_sa(
            log_type="w", message="Get Income -> Requested Incomes does not exist"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Could not find income"
        )

    fun.logger_sa(log_type="i", message="Get Income -> Requested Incomes returned")

    return incomes  # Returning all the incomes


@router.get(
    "/admin/expenditure",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ExpenditureOut],
)
def get_expenditure(
    db: Session = Depends(database.get_db), signup_key=Depends(oauth2.check_signup_key)
):
    """Gets expenditures associated with all the accounts and users"""
    signup_key  # Checking signup key

    expenditures = db.query(models.Expend).all()  # Getting all the expenditures

    if not expenditures:  # Raising an error if expenditures is not found
        fun.logger_sa(
            log_type="w",
            message="Get Expenditures -> Requested Expenditures does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Could not find expenditures"
        )

    fun.logger_sa(
        log_type="i", message="Get Expenditures -> Requested Expenditures returned"
    )

    return expenditures  # Returning all the expenditures


@router.get(
    "/admin/expense",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ExpenseTypeOut],
)
def get_expense_type(
    db: Session = Depends(database.get_db), signup_key=Depends(oauth2.check_signup_key)
):
    """Gets expense types associated with all the accounts and users"""
    signup_key  # Checking signup key

    expense_types = db.query(models.ExpenseType).all()  # Getting all the expense types

    if not expense_types:  # Raising an error if expense types is not found
        fun.logger_sa(
            log_type="w",
            message="Get Expense Types -> Requested Expense Types does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Could not find expense types"
        )

    fun.logger_sa(
        log_type="i", message="Get Expense Types -> Requested Expense Types returned"
    )

    return expense_types  # Returning all the expense types


@router.get(
    "/admin/users",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.SuperAdminUserOut],
)
def get_users(
    db: Session = Depends(database.get_db), signup_key=Depends(oauth2.check_signup_key)
):
    """ "Gets users from all accounts"""
    signup_key  # Checking signup key

    users = db.query(models.User).all()  # Getting all the users

    if not users:  # Raising an error if users is not found
        fun.logger_sa(
            log_type="w", message="Get Users -> Requested users does not exist"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Could not find users"
        )

    fun.logger_sa(log_type="i", message="Get Users -> Requested users returned")

    return users  # Returning all the users


@router.get(
    "/admin/account",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.SuperAdminAccountOut],
)
def get_accounts(
    db: Session = Depends(database.get_db), signup_key=Depends(oauth2.check_signup_key)
):
    """Gets all accounts"""
    signup_key  # Checking signup key

    accounts = db.query(models.Account).all()  # Getting all the accounts

    if not accounts:  # Raising an error if accounts is not found
        fun.logger_sa(
            log_type="w", message="Get Accounts -> Requested accounts does not exist"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Could not find accounts"
        )

    fun.logger_sa(log_type="i", message="Get Accounts -> Requested accounts returned")

    return accounts  # Returning all the accounts
