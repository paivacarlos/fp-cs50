from utils.security import hash_password, check_password


def test_hash_password():
    password = "password"
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert isinstance(hashed_password, str)

    hashed_password2 = hash_password(password)
    assert hashed_password != hashed_password2

def test_check_password():
    password = "password"
    hashed_password = hash_password(password)
    assert check_password(hashed_password, password) is True
    assert check_password(hashed_password, "wrong_password") is False
