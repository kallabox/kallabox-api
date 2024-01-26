from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import time
import api.database as database
import api.schemas as schemas
import api.models as models
import api.utils as utils
import api.oauth2 as oauth2
import api.functions as fun
from uuid import uuid4

router = APIRouter(tags=["Authentication"], prefix="/api")

refresh_token_period = 604800  # seconds in a week


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: schemas.UserLogin,
    db: Session = Depends(database.get_db),
):
    """Check if the username and password are valid and return the JWT Token"""

    account = (
        db.query(models.Account)
        .filter(models.Account.account_name == user_credentials.account_name)
        .first()
    )  # Checking for the requested account

    if account is None:  # Account does not exist
        fun.logger(
            acount_id=str(user_credentials.account_name),
            user_id=str(user_credentials.user_name),
            log_type="c",
            message="Login -> Account does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account does not exist",
        )

    user = (
        db.query(models.User)
        .filter(
            models.User.account_id == account.account_id,
            models.User.user_name == user_credentials.user_name,
        )
        .first()
    )  # Checking for the requested user

    if user is None:  # User in the account does not exist
        fun.logger(
            acount_id=str(account.account_id),
            user_id=str(user_credentials.user_name),
            log_type="c",
            message="Login -> User for the account does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    if not utils.verify(user_credentials.password, user.password):  # Wrong password
        fun.logger(
            acount_id=str(account.account_id),
            user_id=str(user_credentials.user_name),
            log_type="c",
            message="Login -> Incorrect Password",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    refresh_token = (
        fun.create_refresh_token()
    )  # Else create a new refresh token and entering it in the tokens table

    current_time = time.time()
    expiry = current_time + int(refresh_token_period)

    refresh_token_object = models.RefreshToken(
        account_id=user.account_id,
        user_id=user.user_id,
        token_id=uuid4(),
        refreshtoken=refresh_token,
        created_at=current_time,
        expiry=expiry,
    )
    db.add(refresh_token_object)
    db.commit()
    db.refresh(
        refresh_token_object
    )  # Adding the newly created refresh token in the tokens table

    fun.logger(
        account_id=str(user.account_id),
        user_id=str(user.user_id),
        log_type="i",
        message="Login -> User Logged In",
    )

    return {"refresh_token": refresh_token}


@router.get("/refresh", response_model=schemas.RefreshOut)
def refresh_access_token(
    db: Session = Depends(database.get_db),
    refresh_verified=Depends(oauth2.verify_refresh_token),
):
    """Validate whether the refresh token is in the tokens table associated with the user within its exipry and return the newly generated access token"""

    user = (
        db.query(models.User)
        .filter(
            models.User.user_id == refresh_verified.user_id,
            models.User.account_id == refresh_verified.account_id,
        )
        .first()
    )  # Checking if the user exists in the tokens table

    if user is None:  # If user does not exist
        fun.logger(
            account_id=str(refresh_verified.account_id),
            user_id=str(refresh_verified.user_id),
            log_type="w",
            message="Refresh Access Token -> User does not exist",
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    time.sleep(0.5)  # Waiting the program for 500 ms

    data = {
        "account_id": refresh_verified.account_id,
        "account_name": user.account_name,
        "user_id": refresh_verified.user_id,
        "user_name": user.user_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
    }  # Structure of the access token data
    access_token = oauth2.create_access_token(data=data)

    data["access_token"] = access_token

    fun.logger(
        account_id=str(user.account_id),
        user_id=str(user.user_id),
        log_type="i",
        message="Refresh Access Token -> New Access Token Created",
    )

    return data


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    """Logout the user and delete associated refresh token"""

    refresh_token_query = db.query(models.RefreshToken).filter(
        models.RefreshToken.account_id == current_user.account_id,
        models.RefreshToken.user_id == current_user.user_id,
    )  # Searching for the user with the access token

    refresh_token_object = refresh_token_query.first()

    if refresh_token_object is None:  # If no entry in tokens table
        fun.logger(
            account_id=str(current_user.account_id),
            user_id=str(current_user.user_id),
            log_type="w",
            message="Logout -> User does not exist",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )

    refresh_token_query.delete(
        synchronize_session=False
    )  # Deleting the entry in tokens table
    db.commit()

    fun.logger(
        account_id=str(current_user.account_id),
        user_id=str(current_user.user_id),
        log_type="i",
        message="Logout -> User Logged Out",
    )
