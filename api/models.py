from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    UUID,
    Float,
    BigInteger,
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from api.database import Base

### Models for defining the columns of respective tables and obtaining data in database


class Account(Base):
    """Accounts model for accounts table in database"""

    __tablename__ = "accounts"

    ## Specifying columns and datatypes
    account_id = Column(UUID, primary_key=True, nullable=False)
    account_name = Column(String, nullable=False, unique=True)
    status = Column(Boolean, nullable=False, server_default=text("True"))
    timestamp = timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class User(Base):
    """User model for users table in database"""

    __tablename__ = "users"

    ## Specifying column titles and datatypes
    account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
    account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)
    user_id = Column(UUID, primary_key=True, nullable=False)
    user_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    acne = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=True)
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class Income(Base):
    """Income model for income table in database"""

    __tablename__ = "income"

    ## Specifying column titles and datatypes
    account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
    account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(String, ForeignKey("users.user_name"), nullable=False)
    trans_id = Column(UUID, primary_key=True, nullable=False)
    amount = Column(BigInteger, nullable=False)
    method = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, server_default=text("True"))
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Expend(Base):
    """Expenditure model for expend table in database"""

    __tablename__ = "expend"

    ## Specifying column titles and datatypes
    account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
    account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(String, ForeignKey("users.user_name"), nullable=False)
    expend_id = Column(UUID, primary_key=True, nullable=False)
    amount = Column(BigInteger, nullable=False)
    expense_type_id = Column(UUID, nullable=False)
    status = Column(Boolean, nullable=False, server_default=text("True"))
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class ExpenseType(Base):
    """Expense Type model for expense table in database"""

    __tablename__ = "expense"

    ## Specifying column titles and datatypes
    account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
    account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(String, ForeignKey("users.user_name"), nullable=False)
    expense_type_id = Column(UUID, primary_key=True, nullable=False)
    expense_type = Column(String, nullable=False)
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


# class Attachment(Base):
#     """Attachment Type model for attachments table in database"""

#     __tablename__ = "attachments"

#     ## Specifying column titles and datatypes
#     account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
#     user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
#     expend_id = Column(UUID, ForeignKey("expend.expend_id"), nullable=False)
#     attachment_id = Column(UUID, primary_key=True, nullable=False)
#     attachment = Column(String, nullable=True)
#     timestamp = Column(
#         TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
#     )


class RefreshToken(Base):
    """Refresh Token model for tokenstable table in database"""

    __tablename__ = "tokenstable"

    ## Specifying column titles and datatypes

    account_id = Column(UUID, ForeignKey("accounts.account_id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    token_id = Column(UUID, primary_key=True, nullable=False)
    refreshtoken = Column(String, nullable=False)
    created_at = Column(Float, nullable=False)
    expiry = Column(Float, nullable=False)
