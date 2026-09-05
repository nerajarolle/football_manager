import pytest
from nicegui import ui
from nicegui.testing import User
from resources.data import GameState
from resources.helpers import update_fixture_stats

async def _go_to_dashboard(user: User):
    await user.open('/')
    await user.should_see('⚽ ULTIMATE FOOTBALL MANAGER')
    user.find('Start New Career').click()
    await user.should_see('Your Squad')
    

async def test_start_new_game(user: User) -> None:
    await _go_to_dashboard(user)

async def test_user_team_squad_should_have_players(user: User):
    await _go_to_dashboard(user)
    tables = user.find(kind=ui.table).elements
    assert any(len(table.rows) == 19 for table in tables)

async def test_user_sells_player(user: User):
    await _go_to_dashboard(user)
    tables = user.find(kind=ui.table).elements
    visible_tables = [t for t in tables if "data" in t.props]
    assert len(visible_tables) == 1
    squad_table = visible_tables[0]
    assert len(squad_table.rows) == 19
    rows = squad_table.rows
    first_row = rows[0]
    user.find("Sell").trigger("click", args=first_row)
    await user.should_see("Transfer offer")

async def test_result_of_match_is_found_in_fixtures(user: User):
    await _go_to_dashboard(user)
    user.find("Play Next Match").click()
    await user.should_see("Round: 1")
    user.find("Simulate").click()
    await user.should_see("90/90 minutes")
    elements = user.find(ui.label).elements
    home_score = [element for element in elements if "data-home" in element.props][0]
    print(home_score.text)
    away_score = [element for element in elements if "data-away" in element.props][0]
    print(away_score.text)
    user.find("Continue").click()
    await user.should_see("Your Squad")
    user.find("Fixtures").click()
    await user.should_see(f"{home_score.text} - {away_score.text}")

def test_played_fixture_results_are_stored_on_fixture_teams():
    state = GameState()
    state.init_season("London FC")
    fixture = next(fixture for fixture in state.fixtures if fixture.round == 0)

    assert fixture.home is state.teams[fixture.home.name]
    assert fixture.away is state.teams[fixture.away.name]

    fixture.home_score = 2
    fixture.away_score = 1
    update_fixture_stats(fixture, state.teams)

    assert fixture.played is True
    assert fixture.home_score == 2
    assert fixture.away_score == 1
    assert state.teams[fixture.home.name].goals_for == 2
    assert state.teams[fixture.home.name].goals_against == 1
    assert state.teams[fixture.home.name].points == 3
    assert state.teams[fixture.away.name].goals_for == 1
    assert state.teams[fixture.away.name].goals_against == 2
    assert state.teams[fixture.away.name].points == 0



if __name__ == "__main__":
    pytest.main()
