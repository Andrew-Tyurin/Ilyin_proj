from fastapi import HTTPException


def user_not_found_404(user_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"user_id={user_id} not found")


def user_already_exists_400(user_name: str) -> HTTPException:
    return HTTPException(status_code=400, detail=f"user_name={user_name} already exists")


def user_incorrect_data_400() -> HTTPException:
    return HTTPException(status_code=400, detail=f"Incorrect login or password")

