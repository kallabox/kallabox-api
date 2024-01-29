from os import environ


class MissingEnvVariable(Exception):
    pass  # Creating a new child class of Exception


def get_jwt_secret() -> str:
    """Returns the jwt secret from the env variable or raises an exception if not found"""

    try:
        jwt_secret = environ.get("KALLABOX_JWT_SECRET")

        if jwt_secret is None:
            raise MissingEnvVariable("Environment variable for jwt secret not found")

        return str(jwt_secret)

    except KeyError:
        raise MissingEnvVariable("Environment variable for jwt secret not found")

def get_jwt_expiry() -> str:
    """Returns the jwt expiry from the env variable or raises an exception if not found"""

    try:
        jwt_expiry = environ.get("KALLABOX_JWT_EXPIRY")

        if jwt_expiry is None:
            raise MissingEnvVariable("Environment variable for jwt expiry not found")

        return str(jwt_expiry)

    except KeyError:
        raise MissingEnvVariable("Environment variable for jwt expiry not found")


def get_service_token() -> str:
    """Returns the service token from the env variable or raises an exception if not found"""

    try:
        service_token = environ.get("KALLABOX_SERVICE_TOKEN")

        if service_token is None:
            raise MissingEnvVariable("Environment variable for service token not found")

        return str(service_token)

    except KeyError:
        raise MissingEnvVariable("Environment variable for service token not found")


def get_db_host() -> str:
    """Returns the database host from the env variable or raises an exception if not found"""

    try:
        db_host = environ.get("KALLABOX_DB_HOST")

        if db_host is None:
            raise MissingEnvVariable("Environment variable for database host not found")

        return str(db_host)

    except KeyError:
        raise MissingEnvVariable("Environment variable for database host not found")


def get_db_name() -> str:
    """Returns the database name from the env variable or raises an exception if not found"""

    try:
        db_name = environ.get("KALLABOX_DB_NAME")

        if db_name is None:
            raise MissingEnvVariable("Environment variable for database name not found")

        return str(db_name)

    except KeyError:
        raise MissingEnvVariable("Environment variable for database name not found")


def get_db_user() -> str:
    """Returns the database user from the env variable or raises an exception if not found"""

    try:
        db_user = environ.get("KALLABOX_DB_USER")

        if db_user is None:
            raise MissingEnvVariable("Environment variable for database user not found")

        return str(db_user)

    except KeyError:
        raise MissingEnvVariable("Environment variable for databse user not found")


def get_db_password() -> str:
    """Returns the database password from the env variable or raises an exception if not found"""

    try:
        db_pass = environ.get("KALLABOX_DB_PASS")

        if db_pass is None:
            raise MissingEnvVariable(
                "Environment variable for database password not found"
            )

        return str(db_pass)

    except KeyError:
        raise MissingEnvVariable("Environment variable for databse password not found")
