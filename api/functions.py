from fastapi import status, HTTPException
import random
import logging
from os import environ

user_path = environ.get("USER_LOGGER_PATH")
sa_path = environ.get("SA_LOGGER_PATH")


def check_account_name(name: str):
    if name[0].lower() != name[0] or not name[0].isalpha():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Account name should begin with lowercase letters only",
        )  # if the first letter in the account name is of lower case

    if not name.isalnum():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Account name should only contain alphanumeric characters with no spaces",
        )  # Checking for characters other than alphanumeric characters

    return True


def create_refresh_token():
    """Create a new refresh token for the user"""

    base_58_char = list("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    refresh_token = "".join(
        random.choices(base_58_char, k=58)
    )  # Creating a new refresh token using base58

    return refresh_token


def verify_user_role(given, to_check):
    """Given is the user role and to_check is the one it needs to be compared with and checked."""

    if given != "user" and given != "account_admin":  # Invalid role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a valid role"
        )

    if to_check != "user" and to_check != "account_admin":  # Invalid role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a valid role"
        )

    if given != to_check:  # Given role and the actual role are not equal
        return False

    else:
        return True


def convert_to_valid_name(name: str):
    """Function used to convert the expense types' names to valid ones"""
    return name.upper().replace(
        " ", ""
    )  # Stripping the whitespaces and converting to Upper case


def logger(account_id: str, user_id: str, log_type: str, message: str):
    """Logging function to log HTTP requests of users."""

    FORMAT = "%(asctime)s - %(levelname)s - %(account_id)s - %(user_id)s - %(message)s"  # Required format
    dictionary = {"account_id": str(account_id), "user_id": str(user_id)}

    logging.basicConfig(
        format=FORMAT, level=logging.INFO, filename=user_path
    )  # Configuring the logger
    logger = logging.getLogger("apiserver")

    if log_type == "i":  # INFO
        logger.info(msg=message, extra=dictionary)

    elif log_type == "w":  # WARNING
        logger.warning(msg=message, extra=dictionary)

    elif log_type == "e":  # ERROR
        logger.error(msg=message, extra=dictionary)

    elif log_type == "c":  # CRITICAL
        logger.critical(msg=message, extra=dictionary)


def logger_sa(log_type: str, message: str):
    """Logging function to log HTTP requests of super admin."""

    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # Required format

    logging.basicConfig(
        format=FORMAT, level=logging.INFO, filename=sa_path
    )  # Configuring the logger
    logger = logging.getLogger("saserver")

    if log_type == "i":  # INFO
        logger.info(msg=message)

    elif log_type == "w":  # WARNING
        logger.warning(msg=message)

    elif log_type == "e":  # ERROR
        logger.error(msg=message)

    elif log_type == "c":  # CRITICAL
        logger.critical(msg=message)
