import pytest
import allure

from marks import Pages, TestData
from models.enums import CategoryEnum
from models.spend import SpendModel, Category

@allure.epic("niffler-spend")
@allure.feature("Categories controller")
class TestCategoriesController:
    
    @allure.story("Updating Main page data")
    @allure.title("Spending should be deleted after table action")
    @TestData.category(CategoryEnum.GARDEN)
    @TestData.spends(
        SpendModel(amount=18.43,
                   description='Test spending delete',
                   category=Category(name=CategoryEnum.GARDEN),
                   spendDate='2025-10-29T17:39:27.955Z',
                   currency='RUB'
                   )
    )
    @TestData.get_category_data_from_db('Lamaw')
    def test_spending_should_be_deleted_after_table_action(self, category, spends, get_category_data_from_db):
        assert get_category_data_from_db.name == category