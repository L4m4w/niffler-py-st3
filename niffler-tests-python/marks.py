import pytest


class Pages:
    main_page = pytest.mark.usefixtures("main_page")
    registration_page = pytest.mark.usefixtures("registration_page")
    auth_page = pytest.mark.usefixtures("auth_page")
    registration_page_with_different_passwords = pytest.mark.usefixtures("registration_page_with_different_passwords")
    auth_page_with_wrong_password = pytest.mark.usefixtures("auth_page_with_wrong_password")

    profile_page = pytest.mark.usefixtures("profile_page")


class TestData:
    category = lambda x: pytest.mark.parametrize('category', [x], indirect=True)
    spends = lambda x: pytest.mark.parametrize('spends', [x], indirect=True, ids=lambda param: param.description)
    update_profile_name = lambda x: pytest.mark.parametrize('update_profile_name', [x], indirect=True)