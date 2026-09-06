import asyncio
import os
from pathlib import Path
from secrets import choice
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from nicegui import ui
from resources.game_storage import load_from_browser, save_to_browser
from resources.data import GameState
from resources.helpers import (
    complete_market_purchase,
    complete_transfer,
    get_chance_for_event,
    get_market_players,
    get_transfer_buyers,
    get_transfer_offer,
    update_fixture_stats,
)
from resources.objects import Fixture, Player, Team
from resources.variables import (
    DEFAULT_TEAMS,
    TAB_PANEL_HEADER_LABEL_CLASSES,
    TEAM_SQUAD_PANEL_PLAYER_TABLE_COLUMNS,
    TEAM_SQUAD_PANEL_ROW_CLASSES,
)

CLASS_FULL_MB4 = "w-full mb-4"

state = GameState()
GAME_PATH = "/game"
INDEX_FILE = Path(__file__).with_name("index.html")

fastapi_app = FastAPI(title="Football Manager")


@fastapi_app.get("/", include_in_schema=False)
async def landing_page() -> FileResponse:
    return FileResponse(INDEX_FILE, media_type="text/html")


def handle_load_game():
    load_ok = load_from_browser(state)
    if load_ok:
        ui.notify("Game loaded successfully!", type="positive")
        ui.navigate.to(f"{GAME_PATH}/dashboard")
    else:
        ui.notify("No saved game found.", type="negative")


@ui.page(f"{GAME_PATH}/")
def main_menu():
    ui.dark_mode().enable()
    ui.add_head_html("<style>body { background-color: #0f172a; color: white; }</style>")

    with ui.column().classes("w-full h-screen items-center justify-center p-6"):
        ui.label("⚽ ULTIMATE FOOTBALL MANAGER").classes(
            "text-4xl font-extrabold mb-2 text-emerald-400"
        )
        ui.label(
            "Lead your team to glory, buy and sell players, conquer the league!"
        ).classes("text-gray-400 mb-8")

        with ui.card().classes(
            "w-96 p-6 bg-slate-800 shadow-xl border border-slate-700"
        ):
            manager_input = ui.input("Manager Name", value=state.manager_name).classes(
                CLASS_FULL_MB4
            )

            ui.label("Select Team or Create New").classes(
                "font-bold text-sm text-gray-300 mb-1"
            )
            team_choice_type = ui.radio(
                ["Preset Team", "Custom Team"], value="Preset Team"
            ).classes("mb-2")

            team_dropdown = ui.select(DEFAULT_TEAMS, value=DEFAULT_TEAMS[0]).classes(
                CLASS_FULL_MB4
            )
            custom_team_input = ui.input("Custom Team Name").classes(CLASS_FULL_MB4)
            custom_team_input.bind_visibility_from(
                team_choice_type, "value", value="Custom Team"
            )
            team_dropdown.bind_visibility_from(
                team_choice_type, "value", value="Preset Team"
            )

            def start_new_game():
                if not manager_input.value:
                    ui.notify("Manager name is required!", type="negative")
                    return
                state.manager_name = manager_input.value
                tname = (
                    custom_team_input.value
                    if team_choice_type.value == "Custom Team"
                    else team_dropdown.value
                )
                if not tname.strip():
                    ui.notify("Please provide a valid team name", type="negative")
                    return
                state.init_season(tname)
                ui.navigate.to(f"{GAME_PATH}/dashboard")

            ui.button("Start New Career", on_click=start_new_game).classes(
                "w-full bg-emerald-600 hover:bg-emerald-500 font-bold mb-2"
            )
            ui.button("Continue Saved Game", on_click=handle_load_game).classes(
                "w-full bg-slate-700 hover:bg-slate-600"
            )


@ui.page(f"{GAME_PATH}/play")
def play_next_match():
    print(
        f"Current fixture index: {state.current_fixture_idx}, Total rounds: {state.rounds}"
    )
    if state.season_over:
        ui.notify(
            "The season is over! Start a new game to play again.", type="negative"
        )
        return

    if state.current_fixture_idx > state.rounds:
        ui.notify("No more fixtures left in the season.", type="negative")
        return

    this_round_fixtures = [
        f for f in state.fixtures if f.round == state.current_fixture_idx
    ]
    this_round_team_fixture = [
        f for f in this_round_fixtures if state.team_name in [f.home.name, f.away.name]
    ]

    if not this_round_team_fixture:
        ui.notify("Your team does not have a match this round.", type="info")
        state.current_fixture_idx += 1
        return

    fixture = this_round_team_fixture[0]
    other_fixtures = [f for f in this_round_fixtures if f != fixture]

    with ui.dialog().classes("full-width") as match_dialog, ui.card().style('width: 800px; max-width: none;'):
        with ui.column(align_items="stretch").classes("full-width p-4 bg-slate-900 rounded-lg"):
            ui.label(f"Round: {fixture.round + 1}").classes(
                "text-gray-400 text-center mb-4"
            )
            with ui.row(align_items="stretch").classes("w-full justify-between items-center no-wrap"):

                ui.label(f"{fixture.home.name}").classes(
                    "col-5 text-2xl font-bold text-emerald-400 mb-2 text-center"
                )
                score_home = ui.label("0").classes(
                    "col-1 text-4xl font-bold text-center my-2"
                ).props("data-home='score-home'")
                score_away = ui.label("0").classes(
                    "col-1 text-4xl font-bold text-center my-2"
                ).props("data-away='score-away'")
                ui.label(f"{fixture.away.name}").classes(
                    "col-5 text-2xl font-bold text-emerald-400 mb-2 text-center"
                )

            with ui.row().classes("w-full no-wrap") as scorers_row:
                with ui.column().classes("w-full"):
                    for scorer in fixture.home_scorers:
                        ui.label(f"⚽ {scorer}").classes(
                            "text-sm text-gray-400"
                        )
                with ui.column().classes("w-full"):
                    for scorer in fixture.away_scorers:
                        ui.label(f"⚽ {scorer}").classes(
                            "text-sm text-gray-400"
                        )

            def update_scorers(fix: Fixture):
                scorers_row.clear()
                with scorers_row:
                    with ui.column(align_items="start").classes("col-5"):
                        for scorer in fix.home_scorers:
                            ui.label(f"⚽ {scorer}").classes(
                                "text-sm text-gray-400"
                            )
                    ui.column().classes("col-2")
                    with ui.column(align_items="start").classes("col-5"):
                        for scorer in fix.away_scorers:
                            ui.label(f"⚽ {scorer}").classes(
                                "text-sm text-gray-400"
                            )
            # Progress bar for match simulation
            progress_bar = ui.linear_progress(show_value=False).classes("w-full")
            minutes_label = ui.label("0/90 minutes").classes(
                "text-center text-gray-400 text-sm"
            )

            result_label = ui.label().classes(
                "text-lg font-semibold text-emerald-400 mt-4 text-center"
            )

            with ui.button_group():
                start_button = ui.button("Start Match").classes(
                    "w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                )
                simulate_button = ui.button("Simulate", on_click=lambda _, f=fixture: handle_simulate_button(f)).classes("w-full bg-green-600 hover:bg-green-500 text-white font-bold")
                close_button = ui.button("Continue").classes(
                    "w-full bg-blue-600 hover:bg-blue-500 text-white font-bold"
                )
            close_button.enabled = False


            def simulate_minute(fix: Fixture):
                msg = get_chance_for_event(fix)
                update_scorers(fix)
                result_label.text = msg

            def play_other_fixtures():
                for other_fixture in other_fixtures:
                    simulate_match(other_fixture, display_result=False)
                    update_fixture_stats(other_fixture, state.teams)

            def update_all_fixture_stats(fix: Fixture):
                update_fixture_stats(fix, state.teams)
                fix.played = True
                update_scorers(fix)
            
            def simulate_match(fix: Fixture, display_result: bool = True):
                for _minute in range(1, 91):
                    msg = get_chance_for_event(fix)
                    if display_result:
                        update_scorers(fix)
                        result_label.text = msg
                if display_result:
                    minutes_label.text = "90/90 minutes"
                    score_home.text = f"{fix.home_score}"
                    score_away.text = f"{fix.away_score}"
                    close_button.enable()
                    start_button.disable()
                    simulate_button.disable()
                
            
            def handle_simulate_button(fix):
                simulate_match(fix)
                update_all_fixture_stats(fix)
                play_other_fixtures()
            
            
            async def run_match():
                start_button.enabled = False

                # Animate progress bar through 90 minutes
                for minute in range(1, 91):
                    progress_bar.value = minute / 90
                    minutes_label.text = f"{minute}/90 minutes"
                    simulate_minute(fixture)
                    if result_label.text:
                        await asyncio.sleep(1.50)  # Pause to show the event message
                    score_home.text = f"{fixture.home_score}"
                    score_away.text = f"{fixture.away_score}"
                    await asyncio.sleep(0.20)

                # Ensure progress bar reaches exactly 100%
                progress_bar.value = 1.0
                update_all_fixture_stats(fixture)
                play_other_fixtures()

                # Show result
                # result = (
                #     "Draw"
                #     if fixture.home_score == fixture.away_score
                #     else (
                #         fixture.home
                #         if fixture.home_score > fixture.away_score
                #         else fixture.away
                #     )
                # )
                # result_label.text = f"🏆 {result} wins!"
                close_button.enabled = True
                # state.current_fixture_idx += 1

            start_button.on_click(run_match)

            def navigate_to_dashboard():
                match_dialog.close()
                ui.navigate.to(f"{GAME_PATH}/dashboard")

            close_button.on_click(navigate_to_dashboard)

    match_dialog.open()

    state.current_fixture_idx += 1

    if state.current_fixture_idx >= state.rounds:
        state.season_over = True
        ui.notify("The season has ended!", type="info")


@ui.page(f"{GAME_PATH}/dashboard")
def dashboard():
    ui.dark_mode().enable()
    ui.add_head_html("<style>body { background-color: #0f172a; color: white; }</style>")

    if not state.team_name:
        ui.navigate.to(GAME_PATH)
        return

    # Tabs container
    with ui.column().classes("w-full max-w-6xl mx-auto p-4"):
        # Header info
        with ui.row().classes(
            "w-full justify-between items-center bg-slate-800 p-4 rounded-xl border border-slate-700 mb-4"
        ):
            with ui.column():
                ui.label(f"Manager: {state.manager_name}").classes(
                    "text-sm text-gray-400"
                )
                ui.label(f"Team: {state.team_name}").classes(
                    "text-xl font-extrabold text-emerald-400"
                )
            with ui.row().classes("items-center gap-4"):
                ui.label().bind_text_from(
                    state,
                    "budget",
                    backward=lambda b: f"Budget: €{b:,}",
                ).classes("text-green-400 font-bold text-lg")
                ui.button("Play Next Match", on_click=play_next_match).classes(
                    "bg-blue-600 hover:bg-blue-500 text-white font-bold"
                )
                with ui.dropdown_button(text="Options").classes(
                    "bg-slate-800 border border-slate-700 rounded-lg"
                ):
                    ui.label("Options").classes("text-white font-semibold")
                    ui.item("Save Game", on_click=lambda x: save_to_browser(state))
                    ui.item("Quit", on_click=lambda: ui.navigate.to(GAME_PATH))
                # ui.button(
                #     "Save Game", on_click=lambda x: save_to_browser(state)
                # ).classes("bg-blue-600 hover:bg-blue-500")
                # ui.button("Quit", on_click=lambda: ui.navigate.to("/")).classes(
                #     "bg-red-600 hover:bg-red-500"
                # )
        tabs = ui.tabs().classes("w-full bg-slate-800 rounded-t-lg")
        with tabs:
            t_squad = ui.tab("Squad")
            t_market = ui.tab("Transfer Market")
            t_standings = ui.tab("Standings")
            t_fixtures = ui.tab("Fixtures")

        def complete_player_sale(player: Player, buyer: Team, price: int, dialog):
            if state.team is None or not complete_transfer(
                state.team, buyer, player, price
            ):
                ui.notify("That player is no longer available.", type="negative")
                dialog.close()
                return

            if player in state.squad:
                state.squad.remove(player)
            state.budget += price
            dialog.close()
            refresh_squad_table()
            ui.notify(
                f"{player.name} joined {buyer.name} for €{price:,}.",
                type="positive",
            )

        def open_offer_dialog(player: Player, offer_team: Team):
            offer, maximum_offer = get_transfer_offer(offer_team, player)
            sale_offer = {"value": offer}

            with ui.dialog() as dialog:
                with ui.card().classes("w-96 bg-slate-800 text-white"):
                    ui.label("Transfer offer").classes("text-xl font-bold")
                    ui.label(
                        f"{offer_team.name} wants {player.name} for €{offer:,}."
                    ).classes("text-gray-300")
                    offer_label = ui.label().classes("text-amber-300")
                    price_input = ui.number(
                        "Your requested price",
                        value=offer,
                        min=1,
                        max=maximum_offer,
                        step=100000,
                        format="%.0f",
                    ).classes("w-full")
                    with ui.row().classes("w-full justify-end gap-2"):
                        ui.button(
                            "Accept",
                            on_click=lambda: complete_player_sale(
                                player, offer_team, sale_offer["value"], dialog
                            ),
                        ).props("color=positive")
                        ui.button("Reject", on_click=dialog.close).props("flat")

                        def negotiate():
                            requested_price = int(price_input.value or 0)
                            if requested_price <= offer:
                                complete_player_sale(
                                    player, offer_team, requested_price, dialog
                                )
                            elif requested_price <= maximum_offer:
                                sale_offer["value"] = requested_price
                                offer_label.text = (
                                    f"They agree to €{requested_price:,}. Accept to complete the sale."
                                )
                                price_input.value = requested_price
                                price_input.max = requested_price
                            else:
                                sale_offer["value"] = maximum_offer
                                offer_label.text = (
                                    f"They counter with €{maximum_offer:,}. Accept to complete the sale."
                                )
                                price_input.value = maximum_offer

                        ui.button("Negotiate", on_click=negotiate).props(
                            "color=primary"
                        )
            dialog.open()

        def simulate_offer_from_other_team(player: Player):
            other_teams = get_transfer_buyers(state.teams, state.team_name, player)
            if not other_teams:
                ui.notify(f"No offers yet for {player.name}", type="info")
                return
            open_offer_dialog(player, choice(other_teams))

        def handle_player_sale(e):
            print(e.args)
            if state.team is None or not state.team.players:
                return
            player_id = e.args.get("id")
            player = next(
                (candidate for candidate in state.team.players if candidate.id == player_id),
                None,
            )
            if player is None:
                ui.notify("Player not found.", type="negative")
                return
            simulate_offer_from_other_team(player)
        
        with ui.tab_panels(tabs, value=t_squad).classes(
            "w-full bg-slate-900 text-white p-4 rounded-xl border border-slate-700"
        ):
            with ui.tab_panel(t_squad):
                ui.label("Your Squad").classes(TAB_PANEL_HEADER_LABEL_CLASSES)
                with ui.row().classes(TEAM_SQUAD_PANEL_ROW_CLASSES):
                    ui.label(
                        text=f"ATT: {state.team.att} | MID: {state.team.mid} | DEF: {state.team.dfn} | OVERALL: {state.team.overall}"
                    ).classes("text-lg font-semibold")
                    # .bind_text_from(
                    #    state,
                    #    "team",
                    #    backward=lambda t: print(t) f"ATT: {t.team.att} | MID: {t.team.mid} | DEF: {t.team.dfn} | OVERALL: {t.team.overall}",
                    # )

                    ui.label().bind_text_from(
                        state,
                        "team",
                        backward=lambda t: f"Budget: €{t.budget:,}",
                    ).classes("text-lg font-semibold text-amber-400")
                    squad_table = ui.table(
                        columns=TEAM_SQUAD_PANEL_PLAYER_TABLE_COLUMNS,
                        rows=[],
                        row_key="id",
                    ).classes("w-full bg-slate-800 text-white").props('data="squadTable"')
                    
                    with squad_table.add_slot('body-cell-action'):
                        with squad_table.cell('action'):
                            ui.button('Sell', color="white", icon="euro").classes("bg-red").props('flat').on(
                                'click',
                                js_handler='() => emit(props.row)',
                                handler=lambda e: handle_player_sale(e),
                            )
                    # squad_table.add_slot(
                    #     "body-cell-action",
                    #     """<q-td :props="props">
                    #     <q-btn size="sm" color="negative" label="Sell" @click="$parent.$emit('sell_player', props.value)" />
                    #     </q-td>""",
                    # )

                    def refresh_squad_table():
                        # print(state.squad)
                        squad_table.rows = [
                            {
                                "id": p.id,
                                "name": p.name,
                                "pos": p.position,
                                "att": p.att,
                                "mid": p.mid,
                                "dfn": p.dfn,
                                "ovr": p.overall,
                                "value": f"€{p.value:,}",
                            }
                            for p in state.team.players
                        ]

                    # squad_table.on("sell_player", lambda msg: sell_player_handler(msg.args))
                    refresh_squad_table()

            with ui.tab_panel(t_market):
                ui.label("Market").classes(TAB_PANEL_HEADER_LABEL_CLASSES)
                market_container = ui.element("div").classes(
                    "w-full space-y-4 max-h-[600px] overflow-y-auto pr-2"
                )

                def complete_player_purchase(
                    player: Player, owner: Team | None, price: int, dialog
                ):
                    if state.team is None or state.budget < price:
                        ui.notify("Not enough budget for this transfer.", type="negative")
                        return
                    if not complete_market_purchase(
                        state.team, owner, state.transfer_list, player, price
                    ):
                        ui.notify("That player is no longer available.", type="negative")
                        dialog.close()
                        return
                    state.budget -= price
                    dialog.close()
                    refresh_market()
                    refresh_squad_table()
                    ui.notify(
                        f"{player.name} joined your team for €{price:,}.",
                        type="positive",
                    )

                def open_purchase_dialog(player: Player, owner: Team | None):
                    asking_price = player.value if owner is not None else 0
                    minimum_price = int(asking_price * 85 / 100)
                    purchase_price = {"value": asking_price}

                    with ui.dialog() as dialog:
                        with ui.card().classes("w-96 bg-slate-800 text-white"):
                            ui.label("Player purchase").classes("text-xl font-bold")
                            owner_name = owner.name if owner is not None else "Free agent"
                            ui.label(
                                f"{player.name} ({player.position}) - {owner_name}"
                            ).classes("text-gray-300")
                            offer_label = ui.label().classes("text-amber-300")
                            price_input = ui.number(
                                "Your offer",
                                value=asking_price,
                                min=minimum_price,
                                max=max(asking_price, 1),
                                step=100000,
                                format="%.0f",
                            ).classes("w-full")
                            price_input.visible = owner is not None
                            if owner is None:
                                ui.label("This player is available for free.").classes(
                                    "text-emerald-300"
                                )
                            else:
                                def negotiate_purchase():
                                    requested_price = int(price_input.value or 0)
                                    if requested_price < minimum_price:
                                        offer_label.text = (
                                            f"The lowest accepted price is €{minimum_price:,}."
                                        )
                                        price_input.value = minimum_price
                                        return
                                    purchase_price["value"] = requested_price
                                    offer_label.text = (
                                        f"They agree to €{requested_price:,}. Buy to complete the transfer."
                                    )
                                    price_input.max = requested_price

                                ui.button(
                                    "Negotiate", on_click=negotiate_purchase
                                ).props("color=primary")
                            with ui.row().classes("w-full justify-end gap-2"):
                                ui.button(
                                    "Buy Free" if owner is None else "Buy",
                                    on_click=lambda: complete_player_purchase(
                                        player, owner, purchase_price["value"], dialog
                                    ),
                                ).props("color=positive")
                                ui.button("Cancel", on_click=dialog.close).props("flat")
                    dialog.open()

                def refresh_market():
                    market_container.clear()
                    with market_container:
                        market_players = get_market_players(
                            state.teams, state.transfer_list, state.team_name
                        )
                        for player, owner in market_players:
                            market_value = player.value if owner is not None else 0
                            with ui.card().classes(
                                "bg-slate-800 border border-slate-700 w-full p-3"
                            ):
                                with ui.row().classes(
                                    "w-full justify-between items-center"
                                ):
                                    ui.label(player.name).classes(
                                        "font-semibold text-lg"
                                    )
                                    ui.label(f"Position: {player.position}").classes(
                                        "text-sm text-gray-400"
                                    )
                                    ui.label(
                                        f"Team: {owner.name if owner else 'Free agent'}"
                                    ).classes("text-sm text-blue-300")
                                    ui.label(f"Value: €{market_value:,}").classes(
                                        "text-sm text-green-400 font-bold"
                                    )
                                    ui.button(
                                        "Buy",
                                        on_click=lambda x, p=player, o=owner: open_purchase_dialog(p, o),
                                    ).classes(
                                        "bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                                    )

                refresh_market()

            with ui.tab_panel(t_fixtures):
                ui.label("Fixtures").classes(TAB_PANEL_HEADER_LABEL_CLASSES)
                fixtures_container = ui.element("div").classes(
                    "w-full space-y-4 max-h-[600px] overflow-y-auto pr-2"
                )

                def refresh_fixtures():
                    fixtures_container.clear()
                    with fixtures_container:
                        for round_fixture in range(state.rounds):
                            with ui.card().classes(
                                "bg-slate-800 border border-slate-700 w-full p-3"
                            ):
                                ui.label(f"Round {round_fixture + 1}").classes(
                                    "text-lg font-semibold text-emerald-400 mb-2"
                                )
                                for fix in [
                                    f
                                    for f in state.fixtures
                                    if f.round == round_fixture
                                ]:
                                    with ui.row().classes(
                                        "w-full justify-between items-center border-t border-slate-700 pt-2 mt-2"
                                    ):
                                        ui.label(fix.home.name).classes(
                                            "w-1/3 text-right font-medium"
                                        )
                                        score_str = (
                                            f"{fix.home_score} - {fix.away_score}"
                                            if fix.played
                                            else "vs"
                                        )
                                        score_color = (
                                            "text-amber-200 font-bold"
                                            if fix.played
                                            else "text-slate-200"
                                        )
                                        ui.label(score_str).classes(
                                            f"w-1/5 text-center {score_color}"
                                        )
                                        ui.label(fix.away.name).classes(
                                            "w-1/3 text-left font-medium"
                                        )

                refresh_fixtures()

            with ui.tab_panel(t_standings):
                ui.label("Standings").classes(TAB_PANEL_HEADER_LABEL_CLASSES)
                standings_table = ui.table(
                    columns=[
                        {"name": "Team", "label": "Team", "field": "team"},
                        {"name": "P", "label": "P", "field": "p"},
                        {"name": "W", "label": "W", "field": "w"},
                        {"name": "D", "label": "D", "field": "d"},
                        {"name": "L", "label": "L", "field": "l"},
                        {"name": "GF", "label": "GF", "field": "gf"},
                        {"name": "GA", "label": "GA", "field": "ga"},
                        {"name": "PTS", "label": "PTS", "field": "pts"},
                    ],
                    rows=[],
                ).classes("bg-slate-800 text-white")
                # .style("background-color: #f3f4f6; border-collapse: collapse; border: 1px solid #334155;")

                def refresh_standings():
                    standings_table.rows = [
                        {
                            "team": (
                                f"⭐ {tname} ⭐" if tname == state.team_name else tname
                            ),
                            "p": team_data.played,
                            "w": team_data.wins,
                            "d": team_data.draws,
                            "l": team_data.losses,
                            "gf": team_data.goals_for,
                            "ga": team_data.goals_against,
                            "pts": team_data.points,
                            "is_user_team": tname == state.team_name,
                        }
                        for tname, team_data in state.teams.items()
                    ]
                    # Sort by points, then goal difference
                    standings_table.rows.sort(
                        key=lambda x: (x["pts"], x["gf"] - x["ga"]), reverse=True
                    )

                refresh_standings()

def main(port: int = 8000, reload=True):
    ui.run_with(
        fastapi_app,
        title="Football Manager",
        mount_path="/",
        storage_secret="alex-storage",
    )
    if "PYTEST_CURRENT_TEST" not in os.environ:
        server_target = "app:fastapi_app" if reload else fastapi_app
        uvicorn.run(server_target, port=port, reload=reload)

if __name__ in {"__main__", "__mp_main__"}:
    main()
