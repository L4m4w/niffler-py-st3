import time

import pytest
from selene.support.shared import browser
from selene import have, by, be

from marks import Pages, TestData
from models.spend import Spend, Category


@Pages.main_page
def test_spending_title_exists():
    browser.element(by.id("spendings")).should(be.visible)


@Pages.main_page
@TestData.category('school')
@TestData.spends(
    Spend(amount=106.43, description='Test spending delete', category=Category(name='school'),
    # {'name': 'school'},

          spendDate= '2025-10-19T17:39:27.955Z', currency= 'RUB')
)
def test_spending_should_be_deleted_after_table_action(category, spends):
    browser.element('.MuiTable-root tbody').should(have.text('school'))
    browser.element('.MuiTable-root tbody input[type=checkbox').click()
    browser.element('button[id="delete"]').click()

    browser.element('div.MuiDialogActions-root button:nth-child(2)').click()

    browser.element('.MuiBox-root p').should(have.text('There are no spendings'))
