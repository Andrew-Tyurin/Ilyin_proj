status_code_400 = 400
status_code_401 = 401
status_code_404 = 404
status_code_422 = 422

create_user_with_short_password = {"user_name": "test_user1", "password": "12",}
expected_short_password = {'ctx': {'min_length': 4}, 'input': '12', 'loc': ['body', 'password'], 'msg': 'String should have at least 4 characters', 'type': 'string_too_short'}

create_user_with_empty_password = {"user_name": "test_user1", "password": "     ", }
expected_empty_password = {'ctx': {'error': {}}, 'input': '     ', 'loc': ['body', 'password'], 'msg': "Value error, User fields 'password' cannot be empty", 'type': 'value_error'}

create_user_with_short_username = {"user_name": "te", "password": "12345",}
expected_short_username = {'ctx': {'min_length': 3}, 'input': 'te', 'loc': ['body', 'user_name'], 'msg': 'String should have at least 3 characters', 'type': 'string_too_short'}

create_user_with_empty_username = {"user_name": "     ", "password": "12345", }
expected_empty_username = {'ctx': {'error': {}}, 'input': '     ', 'loc': ['body', 'user_name'], 'msg': "Value error, User fields 'user_name' cannot be empty", 'type': 'value_error'}

offset_negative_100 = -100
expected_offset_negative_100 = {'ctx': {'ge': 0}, 'input': '-100', 'loc': ['query', 'offset'], 'msg': 'Input should be greater than or equal to 0', 'type': 'greater_than_equal'}

expected_user_exist = "User 'test_user_1' already exists"

non_user_existent_id = 3
expected_user_by_non_existent_id = 'User id - 3 does not exist'

not_valid_user = {"user_name": "test_user3", "password": "12345",}
expected_user_not_valid_data_authorization = "Incorrect login or password"

user_without_password = {"user_name": "test_user1",}
expected_user_without_password = {'input': {'user_name': 'test_user1'}, 'loc': ['body', 'password'], 'msg': 'Field required', 'type': 'missing'}

expected_not_valid_token = "access-token expired or invalid"

expected_without_token = "Not authenticated"

non_existent_wallet_name = "noname"
expected_without_wallet_name = "Wallet 'noname' does not exist"

not_valid_token = "not_valid_token"

create_wallet_balance_negative_100 = {"name": "SBER", "initial_balance": -100}
expected_create_wallet_balance_negative_100 = {'ctx': {'ge': 0}, 'input': -100, 'loc': ['body', 'initial_balance'], 'msg': 'Input should be greater than or equal to 0', 'type': 'greater_than_equal'}

expected_wallet_exist = "Wallet 'SBER' already exists"


wallet_add_negative_amount = {
    "wallet_name": "SBER",
    "amount": -100,
    "description": "test-text"
}
expected_wallet_add_negative_amount = {'ctx': {'ge': 1}, 'input': -100, 'loc': ['body', 'amount'], 'msg': 'Input should be greater than or equal to 1', 'type': 'greater_than_equal'}

wallet_add_expense_greater_balance = {
    "wallet_name": "SBER",
    "amount": 1000,
    "description": "test-text"
}

expected_wallet_add_expense_greater_balance_chunk_1 = "Problem updating object wallet_name='SBER'"
expected_wallet_add_expense_greater_balance_chunk_2 = "DETAIL:  Failing row contains (1, SBER, -600, 1)."
