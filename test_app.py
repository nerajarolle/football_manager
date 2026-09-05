import pytest
from nicegui import ui
from nicegui.testing import User



async def test_start_new_game(user: User) -> None:
    await user.open('/')
    await user.should_see('⚽ ULTIMATE FOOTBALL MANAGER')
    user.find('Start New Career').click()
    await user.should_see('Your Squad')

async def test_user_team_squad_should_have_players(user: User):
    await user.open('/')
    await user.should_see('⚽ ULTIMATE FOOTBALL MANAGER')
    user.find('Start New Career').click()
    await user.should_see('Your Squad')
    tables = user.find(kind=ui.table).elements
    assert any(len(table.rows) == 19 for table in tables)

async def test_user_sells_player(user: User):
    await user.open('/')
    await user.should_see('⚽ ULTIMATE FOOTBALL MANAGER')
    user.find('Start New Career').click()
    await user.should_see('Your Squad')
    tables = user.find(kind=ui.table).elements
    visible_tables = [t for t in tables if "data" in t.props]
    assert len(visible_tables) == 1
    squad_table = visible_tables[0]
    assert len(squad_table.rows) == 19
    rows = squad_table.rows
    first_row = rows[0]
    user.find("Sell").trigger("click", args=first_row)
    await user.should_see("Transfer offer")


if __name__ == "__main__":
    pytest.main()
