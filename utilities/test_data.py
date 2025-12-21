class TestData:
    VALID_USERS = [
        ("standard_user", "secret_sauce"),
        ("probl2em_user", "sec2ret_sauce"),
        ("performance_glitch_user", "secret_sauce")
    ]
    
    INVALID_LOGIN_DATA = [
        ("locked_out_user", "secret_sauce", "LOCKED"),
        ("standard_user", "wrong_password", "INVALID"),
        ("not_exist_user", "secret_sauce", "INVALID")
    ]