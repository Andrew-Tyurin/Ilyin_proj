from datetime import date
from app.domain.rules import UserRules, WalletOperationRules, WalletRules

status_code_201 = 201
status_code_400 = 400
status_code_401 = 401
status_code_404 = 404
status_code_422 = 422
status_code_409 = 409

create_user_with_short_password = {"user_name": "test_user1", "password": "12",}
expected_short_password = {'ctx': {'min_length': UserRules.password_min_length}, 'input': '12', 'loc': ['body', 'password'], 'msg': f'String should have at least {UserRules.password_min_length} characters', 'type': 'string_too_short'}

create_user_with_empty_password = {"user_name": "test_user1", "password": "     ", }
expected_empty_password = {'ctx': {'error': {}}, 'input': '     ', 'loc': ['body', 'password'], 'msg': "Value error, User fields 'password' cannot be empty", 'type': 'value_error'}

create_user_with_short_username = {"user_name": "te", "password": "12345",}
expected_short_username = {'ctx': {'min_length': UserRules.user_name_min_length}, 'input': 'te', 'loc': ['body', 'user_name'], 'msg': f'String should have at least {UserRules.user_name_min_length} characters', 'type': 'string_too_short'}

create_user_with_empty_username = {"user_name": "     ", "password": "12345", }
expected_empty_username = {'ctx': {'error': {}}, 'input': f'{create_user_with_empty_username["user_name"]}', 'loc': ['body', 'user_name'], 'msg': "Value error, User fields 'user_name' cannot be empty", 'type': 'value_error'}

offset_negative_100 = -100
expected_offset_negative_100 = {'ctx': {'ge': 0}, 'input': str(offset_negative_100), 'loc': ['query', 'offset'], 'msg': f'Input should be greater than or equal to 0', 'type': 'greater_than_equal'}

exists_user_name = 'test_user_1'
expected_user_exist = f"User user_name='{exists_user_name}' already exists"

non_user_existent_id = 3
expected_user_by_non_existent_id = f"User user_id={non_user_existent_id} not found"

not_valid_user = {"user_name": "test_user3", "password": "12345",}
expected_user_not_valid_data_authorization = "Incorrect login or password"

user_without_password = {"user_name": "test_user1",}
expected_user_without_password = {'input': user_without_password, 'loc': ['body', 'password'], 'msg': 'Field required', 'type': 'missing'}

expected_not_valid_token = "access-token expired or invalid"

expected_without_token = "Not authenticated"

non_existent_wallet_name = "noname"
expected_without_wallet_name = f"Wallet wallet_name='{non_existent_wallet_name}' does not exist"

not_valid_token = "not_valid_token"

create_wallet_non_existent_currency = {"name": "SBER", "currency": 'twd'}
expected_wallet_non_existent_currency = {'ctx': {'expected': "'rub', 'usd' or 'eur'"}, 'input': 'twd', 'loc': ['body', 'currency'], 'msg': "Input should be 'rub', 'usd' or 'eur'", 'type': 'enum'}

wallet_exist_name = 'SBER'
expected_wallet_exist = f"Wallet wallet_name='{wallet_exist_name}' already exists"

create_wallets_overflow = [{"name": f"SBER{i}", "currency": 'rub'} for i in range(WalletRules.max_amount_wallets + 1)]
expected_response_wallets_overflow = f"The maximum number of wallets you can create is: {WalletRules.max_amount_wallets}"

exist_wallet_id = 1
wallet_add_negative_amount = {
    "wallet_id": exist_wallet_id,
    "amount": -100,
    "description": "test-text"
}
wallet_add_income_zero_balance = {
    "wallet_id": exist_wallet_id,
    "amount": 0,
    "description": "test-text"
}
expected_wallet_add_negative_amount = {'ctx': {'ge': 0.01}, 'input': wallet_add_negative_amount["amount"], 'loc': ['body', 'amount'], 'msg': 'Input should be greater than or equal to 0.01', 'type': 'greater_than_equal'}
expected_wallet_add_zero_amount = {'ctx': {'ge': 0.01}, 'input': wallet_add_income_zero_balance["amount"], 'loc': ['body', 'amount'], 'msg': 'Input should be greater than or equal to 0.01', 'type': 'greater_than_equal'}

wallet_add_income_greater_balance = {
    "wallet_id": exist_wallet_id,
    "amount": 100_000_000_000_000,
    "description": "test-text"
}
wallet_add_expense_greater_balance = {
    "wallet_id": exist_wallet_id,
    "amount": 1000,
    "description": "test-text"
}
transfer_wallets_insufficient_funds = {
    "from_wallet_id": 1,
    "to_wallet_id": 2,
    "amount": 10_000,
}
expected_wallet_greater_or_less_balance = f"Wallet wallet_id={exist_wallet_id} balance cannot be less than zero and more {WalletOperationRules.amount_max}"

transfer_not_valid_between_wallets = {
    "from_wallet_id": 1,
    "to_wallet_id": 1,
    "amount": 100,
}
expected_transfer_not_valid_between_wallets = {'ctx': {'error': {}}, 'input': 1, 'loc': ['body', 'to_wallet_id'], 'msg': 'Value error, same wallets ids; (from_wallet_id=1) == (to_wallet_id=1) - unacceptable', 'type': 'value_error'}

non_existent_wallet_id = 10
expected_not_exist_wallet_id = f"Wallet wallet_id={non_existent_wallet_id} does not exist"

non_existent_order_by_data = 'non-value'
expected_non_existent_order_by_data = {'ctx': {'expected': "'increase' or 'decrease'"}, 'input': 'non-value', 'loc': ['query', 'order_by_data'], 'msg': "Input should be 'increase' or 'decrease'", 'type': 'enum'}

params_create_pdf_more_n_days = {"date_from": "2025-01-01", "date_to": "2026-01-02", "timezone": "Europe/Moscow"}
date_from = date(*(map(int, params_create_pdf_more_n_days['date_from'].split('-'))))
date_to = date(*(map(int, params_create_pdf_more_n_days['date_to'].split('-'))))
more_days = (date_to - date_from).days
expected_create_pdf_more_n_days = f"Value error, The range is too wide; you have {more_days} days, but it should be no more than {WalletOperationRules.file_in_interval_days} days."

params_create_pdf_not_valid_timezone = {"date_from": "2026-01-01", "date_to": "2026-01-01", "timezone": "Mars/Venera"}
expected_create_pdf_not_valid_timezone = "Value error, Unknown timezone"

params_create_pdf_date_from_more_date_to = {"date_from": "2026-01-01", "date_to": "2025-01-01", "timezone":"Europe/Moscow"}
expected_create_pdf_date_from_more_date_to = "Value error, date_from must be less date_to"
