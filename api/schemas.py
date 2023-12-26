from pydantic import BaseModel, EmailStr, PositiveInt, UUID4
from datetime import datetime

## 1) Tokens


class TokenData(BaseModel):  # Verification
    """Token Data validation class for output JWT token attributes"""

    account_id: UUID4
    account_name: str
    user_id: UUID4
    user_name: str
    email: EmailStr
    phone: int
    role: str
    access_token: str


class Token(BaseModel):  # Response Model
    """Token validation Class for logging in users' JWT and Refresh Token issue."""

    refresh_token: str


# 2) Income Models


class IncomeIn(BaseModel):  # Input Model
    """Validation Class for input attributes to adding income data."""

    amount: PositiveInt
    method: str


class IncomeOut(BaseModel):  # Response Model
    """Validation Class for output attributes of income."""

    account_name: str
    user_name: str
    trans_id: UUID4
    amount: PositiveInt
    method: str
    status: bool
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class IncomeUpdateIn(BaseModel):  # Input Model
    """Validation Class for input attributes for updating income."""

    trans_id: UUID4
    amount: PositiveInt


# 3) User


class UserCredentials(BaseModel):  # Input Model
    """Validation class for input attributes to create a new user."""

    user_name: str
    email: EmailStr
    phone: str
    password: str
    role: str


class UserOut(BaseModel):  # Response Model
    """Validation class for output attributes after creating a new user."""

    account_id: UUID4
    user_id: UUID4
    email: EmailStr
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class UserLogin(BaseModel):  # Input Model
    """Validation class for input attributes to log in."""

    account_name: str
    user_name: str
    password: str


## 4) Expenditure


class ExpenditureOut(BaseModel):  # Response Model
    """Validation class for output attributes of expenditure."""

    account_name: str
    user_name: str
    expend_id: UUID4
    amount: int
    expense_type_id: UUID4
    status: bool
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class ExpenditureCreate(BaseModel):  # Input Model
    """Validation class for input attributes of creating a expenditure."""

    amount: int
    expense: str


class ExpenditureUpdateIn(BaseModel):  # Input Model
    """Validation class for input attributes of updating an existing expenditure."""

    expend_id: UUID4
    amount: PositiveInt
    expense: str


# 5) Expense Type


class ExpenseTypeIn(BaseModel):  # Input Model
    """Validation class for input attributes of creating an expense type."""

    expense_type: str


class ExpenseTypeOut(BaseModel):  # Response Model
    """Validation class for output attributes after creating an expense type."""

    account_name: str
    user_name: str
    expense_type_id: UUID4
    expense_type: str
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class ExpenseTypeUpdateIn(BaseModel):  # Input Model
    """Validation class for input attributes for updating an existing expense type."""

    expense_type_id: UUID4
    expense_type: str


# 6) Refresh Token


class RefreshOut(BaseModel):  # Response Model
    """Validation class for output attributes after refreshing an access token."""

    access_token: str
    account_id: UUID4
    user_id: UUID4
    user_name: str
    email: EmailStr
    phone: str
    role: str

    class Config:  # Necessary for returning
        orm_mode = True


# 7) Account


class AccountUserDeleteIn(BaseModel):  # Input Model
    """Validation class for input attribute to delete an user from an account."""

    user_name: str


class AccountIn(BaseModel):  # Input Model
    """Validation class for input attributes to create an account."""

    account_name: str
    user_name: str
    email: EmailStr
    phone: str
    password: str


class AccountOut(BaseModel):  # Response Model
    """Validation class for output attributes after creating an account."""

    account_id: UUID4
    account_name: str
    user_id: UUID4
    user_name: str
    email: EmailStr
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class AccountUserUpdateOut(UserOut):  # Response Model
    """Validation class for output attributes after updating an existing account user inheriting from the UserOut Class."""

    email: EmailStr
    user_id: UUID4
    role: str


class AccountUserUpdateIn(BaseModel):  # Input Model
    """Validation class for input attributes to update an existing user's role."""

    user_name: str
    role: str


class AccountUserOut(UserOut):  # Response Model
    """Validation class for output attributes for users in an account."""

    account_name: str
    user_name: str
    role: str


# 7) Super Admin


class SuperAdminUserOut(BaseModel):  # Response Model
    """Validation class for output attributes of all users."""

    account_id: UUID4
    account_name: str
    user_id: UUID4
    user_name: str
    email: EmailStr
    phone: int
    role: str
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True


class SuperAdminUserUpdateIn(BaseModel):  # Input Model
    """Validation class for input attributes of updating an existing user."""

    user_name: str
    account_name: str
    role: str


class SuperAdminAccountDelete(BaseModel):  # Input Model
    """Validation class for input attribute to delete an existing account."""

    account_name: str


class SuperAdminUserDelete(BaseModel):  # Input Model
    """Validation class for input attributes to delete an existing user."""

    account_name: str
    user_name: str


class SuperAdminAccountOut(BaseModel):  # Response Model
    """Validation class for output attributes of all accounts."""

    account_id: UUID4
    account_name: str
    status: bool
    timestamp: datetime

    class Config:  # Necessary for returning
        orm_mode = True
