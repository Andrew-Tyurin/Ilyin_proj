from fastapi import HTTPException

from app.domain.rules import WalletRules


def user_not_found_404(user_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"User {user_id=} not found")


def user_already_exists_409(user_name: str) -> HTTPException:
    return HTTPException(status_code=409, detail=f"User {user_name=} already exists")


def user_incorrect_data_400() -> HTTPException:
    return HTTPException(status_code=400, detail=f"Incorrect login or password")


def wallet_not_found_name_404(wallet_name: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Wallet {wallet_name=} does not exist")


def wallet_not_found_id_404(wallet_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Wallet {wallet_id=} does not exist")


def wallet_already_exists_409(wallet_name: str) -> HTTPException:
    return HTTPException(status_code=409, detail=f"Wallet {wallet_name=} already exists")


def wallet_not_valid_balance_400(wallet_id: int) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"Wallet {wallet_id=} balance cannot be less than zero and more {WalletRules.balance_max}"
    )


def wallet_creation_limit_has_been_exceeded_422():
    return HTTPException(
        status_code=422,
        detail=f"The maximum number of wallets you can create is: {WalletRules.max_amount_wallets}"
    )
