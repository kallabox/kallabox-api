from jose import JWTError, jwt
from datetime import datetime, timedelta
import time
import api.schemas as schemas
import api.models as models
import api.database as database
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import api.config as config
from uuid import UUID


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

jwt_secret = config.get_jwt_secret()
jwt_algo = "HS256"
jwt_expiry = config.get_jwt_expiry()

signup_key = config.get_service_token()


def create_access_token(data: dict):
    """Creates a jwt token after the user has logged in and returns it"""
    data["user_id"] = str(data["user_id"])
    data["account_id"] = str(data["account_id"])
    data["phone"] = str(data["phone"])
    to_encode = data.copy()  # input variable data has the id of the user
    expire = datetime.utcnow() + timedelta(minutes=int(jwt_expiry))  # expire time
    to_encode.update({"exp": expire})  # updating the dictionary
    encoded_jwt = jwt.encode(
        to_encode, jwt_secret, algorithm=jwt_algo
    )  # creating a jwt token
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify if the given access token is a valid and authorized one"""

    try:
        payload = jwt.decode(
            token, jwt_secret, algorithms=[jwt_algo]
        )  # Decrypting the payload

        account_id: str = payload.get("account_id")
        account_name: str = payload.get("account_name")
        user_id: str = payload.get("user_id")
        user_name: str = payload.get("user_name")
        email: str = payload.get("email")
        phone: str = payload.get("phone")
        role: str = payload.get("role")

        if user_id is None:  # No user is present
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = schemas.TokenData(
            account_id=UUID(account_id),
            account_name=account_name,
            user_id=UUID(user_id),
            user_name=user_name,
            email=email,
            phone=int(phone),
            role=role,
            access_token=token,
        )

    except JWTError:  # Could not validate JWT token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def check_signup_key(signup_token: str = Depends(oauth2_scheme)):
    """Check signup key for super admin user"""
    try:
        signup_key == signup_token  # Trying if the signup key is the same as the signup token
        return True

    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Signup Key"
        )


def verify_refresh_token(
    db: Session = Depends(database.get_db), refresh_token: str = Depends(oauth2_scheme)
):
    """Verify whether the refresh token is a valid one"""

    refresh_token_object = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.refreshtoken == refresh_token)
        .first()
    )  # Finding a refresh token object in the tokens table

    if (
        refresh_token_object is None
    ):  # If refresh token is not present in the tokens table
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Refresh Token"
        )

    current_time = time.time()  # Current time

    if (
        current_time > refresh_token_object.expiry
    ):  # if the expiry time is less than the current time
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token Expired"
        )

    return refresh_token_object
