class TestData:
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("problem_user", "secret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]
    
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", "LOCKED"),
        ("standard_user", "wrong_password", "INVALID"),
        ("not_exist_user", "secret_sauce", "INVALID")
    ]