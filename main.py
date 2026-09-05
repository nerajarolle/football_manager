import asyncio
import json
from random import randint
from secrets import choice
from nicegui import ui

# --- DATA MODELS & LOGIC ---

POSITIONS = ["GK", "DEF", "MID", "ATT"]
FIRST_NAMES = [
    "James",
    "John",
    "Robert",
    "Michael",
    "William",
    "David",
    "Richard",
    "Joseph",
    "Thomas",
    "Charles",
    "Daniel",
    "Matthew",
    "Anthony",
    "Mark",
    "Donald",
    "Steven",
    "Paul",
    "Andrew",
    "Joshua",
    "Kenneth",
]
LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Miller",
    "Davis",
    "Garcia",
    "Rodriguez",
    "Wilson",
    "Martinez",
    "Anderson",
    "Taylor",
    "Thomas",
    "Hernandez",
    "Moore",
    "Martin",
    "Jackson",
    "Thompson",
    "White",
]

DEFAULT_TEAMS = [
    "London FC",
    "Manchester United",
    "Madrid Whites",
    "Catalonia Blaugrana",
    "Bavaria Munich",
    "Parisian Club",
    "Turin Old Lady",
    "Milan Red",
]

import uuid
import random
from typing import List

class Player:
    def __init__(self, name: str, position: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.position = position  # 'ATT', 'MID', 'DEF'
        
        # Genera attributi casuali basati sulla posizione
        if position == 'ATT':
            self.att = random.randint(70, 95)
            self.mid = random.randint(50, 75)
            self.dfn = random.randint(30, 55)
        elif position == 'MID':
            self.att = random.randint(60, 85)
            self.mid = random.randint(70, 95)
            self.dfn = random.randint(60, 85)
        else: # DEF
            self.att = random.randint(30, 55)
            self.mid = random.randint(50, 75)
            self.dfn = random.randint(70, 95)
            
        self.overall = round((self.att + self.mid + self.dfn) / 3)
        self.value = self.overall * random.randint(250_000, 400_000)

class Team:
    def __init__(self, name: str, is_user: bool = False):
        self.id = str(uuid.uuid4())
        self.name = name
        self.is_user = is_user
        self.budget = 50_000_000 if is_user else 0
        self.players: List[Player] = []
        
        # Statistiche della classifica di campionato
        self.played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0
        self.gd = 0
        self.points = 0
        
        # Genera automaticamente una rosa iniziale di 15 giocatori
        self._generate_initial_squad()

    def _generate_initial_squad(self):
        first_names = ["Luca", "Marco", "Alessandro", "Giovanni", "Roberto", "Mario", "Stefano", "Francesco", "David", "John", "Paul", "Robert"]
        last_names = ["Rossi", "Ferrari", "Russo", "Bianchi", "Romano", "Colombo", "Ricci", "Smith", "Jones", "Miller", "Davis", "Wilson"]
        
        # Assegna 4 Attaccanti, 6 Centrocampisti, 5 Difensori
        positions = ['ATT'] * 4 + ['MID'] * 6 + ['DEF'] * 5
        for pos in positions:
            full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
            self.players.append(Player(full_name, pos))

    # Proprietà dinamiche calcolate sulla media dei giocatori in rosa
    @property
    def att(self) -> int:
        att_players = [p.att for p in self.players if p.position == 'ATT']
        return round(sum(att_players) / len(att_players)) if att_players else 50

    @property
    def mid(self) -> int:
        mid_players = [p.mid for p in self.players if p.position == 'MID']
        return round(sum(mid_players) / len(mid_players)) if mid_players else 50

    @property
    def dfn(self) -> int:
        dfn_players = [p.dfn for p in self.players if p.position == 'DEF']
        return round(sum(dfn_players) / len(dfn_players)) if dfn_players else 50

    @property
    def overall(self) -> int:
        return round((self.att + self.mid + self.dfn) / 3)

class Fixture:
    def __init__(self, home: Team, away: Team):
        self.id = str(uuid.uuid4())
        self.home = home
        self.away = away
        self.home_score = 0
        self.away_score = 0
        self.played = False


def generate_player(pos=None):
    if not pos:
        pos = choice(POSITIONS)
    name = f"{choice(FIRST_NAMES)} {choice(LAST_NAMES)}"
    # Attributes 50-99
    pace = randint(50, 99)
    shooting = randint(40, 99) if pos != "GK" else randint(1, 20)
    passing = randint(50, 99)
    defending = randint(50, 99) if pos != "GK" else randint(60, 99)
    gk_skill = randint(60, 99) if pos == "GK" else randint(1, 30)

    if pos == "GK":
        overall = int((gk_skill * 0.7) + (passing * 0.3))
    elif pos == "DEF":
        overall = int((defending * 0.5) + (pace * 0.3) + (passing * 0.2))
    elif pos == "MID":
        overall = int(
            (passing * 0.4) + (pace * 0.3) + (defending * 0.2) + (shooting * 0.1)
        )
    else:  # ATT
        overall = int((shooting * 0.5) + (pace * 0.3) + (passing * 0.2))

    value = overall * 150000
    player = Player(name=name, position=pos)
    player.value = value
    player.overall = overall
    player.att = shooting
    player.dfn = defending
    player.mid = passing
    return player
    # return {
    #     "name": name,
    #     "position": pos,
    #     "pace": pace,
    #     "shooting": shooting,
    #     "passing": passing,
    #     "defending": defending,
    #     "gk": gk_skill,
    #     "overall": overall,
    #     "value": value,
    # }


def generate_team_squad():
    squad = []
    # 2 GKs, 6 DEFs, 6 MIDs, 4 ATTs = 18 players
    for _ in range(2):
        squad.append(generate_player("GK"))
    for _ in range(6):
        squad.append(generate_player("DEF"))
    for _ in range(6):
        squad.append(generate_player("MID"))
    for _ in range(4):
        squad.append(generate_player("ATT"))
    return squad


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.manager_name = "Coach"
        self.team_name = ""
        self.team = None
        self.budget = 20000000
        self.squad = []
        self.transfer_list = []
        self.teams = {}  # name -> {squad, p, w, d, l, gf, ga, pts}
        self.fixtures = []
        self.current_fixture_idx = 0
        self.season_over = False
        self.refresh_transfer_market()

    def refresh_transfer_market(self):
        self.transfer_list = [generate_player() for _ in range(8)]

    def init_season(self, user_team_name):
        self.team_name = user_team_name
        self.team = Team(name=user_team_name, is_user=True)
        self.budget = 25000000
        self.squad = generate_team_squad()
        self.season_over = False
        self.current_fixture_idx = 0

        # Populate league teams
        all_team_names = list(DEFAULT_TEAMS)
        if self.team_name not in all_team_names:
            all_team_names[0] = self.team_name  # Replace first if custom
        else:
            all_team_names.remove(self.team_name)
            all_team_names.insert(0, self.team_name)

        self.teams = {}
        for t in all_team_names:
            squad = self.squad if t == self.team_name else generate_team_squad()
            self.teams[t] = {
                "squad": squad,
                "p": 0,
                "w": 0,
                "d": 0,
                "l": 0,
                "gf": 0,
                "ga": 0,
                "pts": 0,
            }

        # Generate Double Round-Robin fixtures
        self.fixtures = []
        team_list = list(self.teams.keys())
        # Simple round-robin scheduling
        n = len(team_list)
        rounds = []
        for r in range(n - 1):
            round_fixtures = []
            for i in range(n // 2):
                t1 = team_list[i]
                t2 = team_list[n - 1 - i]
                if i == 0 and r % 2 == 1:
                    round_fixtures.append((t2, t1))
                else:
                    round_fixtures.append((t1, t2))
            team_list.insert(1, team_list.pop())
            rounds.append(round_fixtures)

        # First half
        for rnd in rounds:
            for h, a in rnd:
                self.fixtures.append(
                    {
                        "home": h,
                        "away": a,
                        "played": False,
                        "home_score": 0,
                        "away_score": 0,
                        "commentary": [],
                    }
                )
        # Second half (reverse fixtures)
        second_half = []
        for rnd in rounds:
            rnd_rev = []
            for h, a in rnd:
                rnd_rev.append((a, h))
            second_half.append(rnd_rev)
        for rnd in second_half:
            for h, a in rnd:
                self.fixtures.append(
                    {
                        "home": h,
                        "away": a,
                        "played": False,
                        "home_score": 0,
                        "away_score": 0,
                        "commentary": [],
                    }
                )

    def get_team_overall(self, tname):
        squad = self.teams[tname]["squad"]
        if not squad:
            return 60
        return int(sum(p["overall"] for p in squad) / len(squad))


state = GameState()


# --- LOCALSTORAGE BRIDGE ---
async def save_to_browser():
    data = {
        "manager_name": state.manager_name,
        "team_name": state.team_name,
        "budget": state.budget,
        "squad": state.squad,
        "transfer_list": state.transfer_list,
        "teams": state.teams,
        "fixtures": state.fixtures,
        "current_fixture_idx": state.current_fixture_idx,
        "season_over": state.season_over,
    }
    json_str = json.dumps(data)
    await ui.run_javascript(
        f"localStorage.setItem('football_manager_save', {json.dumps(json_str)});"
    )
    ui.notify("Game saved successfully!", type="positive")


async def load_from_browser():
    res = await ui.run_javascript("localStorage.getItem('football_manager_save');")
    if res:
        data = json.loads(res)
        state.manager_name = data["manager_name"]
        state.team_name = data["team_name"]
        state.budget = data["budget"]
        state.squad = data["squad"]
        state.transfer_list = data["transfer_list"]
        state.teams = data["teams"]
        state.fixtures = data["fixtures"]
        state.current_fixture_idx = data["current_fixture_idx"]
        state.season_over = data["season_over"]
        ui.notify("Game loaded successfully!", type="positive")
        ui.navigate.reload()
    else:
        ui.notify("No saved game found.", type="warning")


# --- UI VIEWS ---
@ui.page("/")
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
                "w-full mb-4"
            )

            ui.label("Select Team or Create New").classes(
                "font-bold text-sm text-gray-300 mb-1"
            )
            team_choice_type = ui.radio(
                ["Preset Team", "Custom Team"], value="Preset Team"
            ).classes("mb-2")

            team_dropdown = ui.select(DEFAULT_TEAMS, value=DEFAULT_TEAMS[0]).classes(
                "w-full mb-4"
            )
            custom_team_input = ui.input("Custom Team Name").classes("w-full mb-4")
            custom_team_input.bind_visibility_from(
                team_choice_type, "value", value="Custom Team"
            )
            team_dropdown.bind_visibility_from(
                team_choice_type, "value", value="Preset Team"
            )

            def start_new_game():
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
                ui.navigate.to("/dashboard")

            ui.button("Start New Career", on_click=start_new_game).classes(
            "w-full bg-emerald-600 hover:bg-emerald-500 font-bold mb-2"
            )
            ui.button("Continue Saved Game", on_click=load_from_browser).classes(
            "w-full bg-slate-700 hover:bg-slate-600"
            )


@ui.page("/dashboard")
def dashboard():
    ui.dark_mode().enable()
    ui.add_head_html("<style>body { background-color: #0f172a; color: white; }</style>")

    if not state.team_name:
        ui.navigate.to("/")
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
                budget_lbl = ui.label(f"Budget: €{state.budget:,}").classes(
                    "text-green-400 font-bold text-lg"
                )
                ui.button("Save Game", on_click=save_to_browser).classes(
                    "bg-blue-600 hover:bg-blue-500"
                )
                ui.button("Quit", on_click=lambda: ui.navigate.to("/")).classes(
                    "bg-red-600 hover:bg-red-500"
                )

        tabs = ui.tabs().classes("w-full bg-slate-800 rounded-t-lg")
        with tabs:
            t_squad = ui.tab("Squad")
            t_market = ui.tab("Transfer Market")
            t_standings = ui.tab("Standings")
            t_fixtures = ui.tab("Fixtures")

        with ui.tab_panels(tabs, value=t_squad).classes(
            "w-full bg-slate-900 text-white p-4 rounded-xl border border-slate-700"
        ):
            # --- SQUAD TAB ---
            with ui.tab_panel(t_squad):
                ui.label("Your Squad").classes(
                    "text-2xl font-bold mb-4 text-emerald-400"
                )

                # Team Attributes Summary
                with ui.row().classes(
                    "w-full justify-between items-center bg-slate-800 p-4 rounded-lg mb-4 border border-slate-700"
                ):

                    def update_squad_stats():
                        team = state.team
                        return f"ATT: {team.att} | MID: {team.mid} | DEF: {team.dfn} | OVERALL: {team.overall}"

                    ui.label().bind_text_from(
                        state,
                        "team",
                        backward=lambda t: f"ATT: {t.att} | MID: {t.mid} | DEF: {t.dfn} | OVERALL: {t.overall}",
                    ).classes("text-lg font-semibold")
                    ui.label().bind_text_from(
                        state,
                        "team",
                        backward=lambda t: f"Budget: €{t.budget:,}",
                    ).classes("text-lg font-semibold text-amber-400")

                    # Squad Table
                    columns = [
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "required": True,
                            "align": "left",
                        },
                        {
                            "name": "pos",
                            "label": "Position",
                            "field": "position",
                            "align": "center",
                        },
                        {"name": "att", "label": "ATT", "field": "att", "sortable": True},
                        {"name": "mid", "label": "MID", "field": "mid", "sortable": True},
                        {"name": "dfn", "label": "DEF", "field": "dfn", "sortable": True},
                        {"name": "ovr", "label": "OVR", "field": "ovr", "sortable": True},
                        {
                            "name": "value",
                            "label": "Value",
                            "field": "value",
                            "sortable": True,
                        },
                        {
                            "name": "action",
                            "label": "Action",
                            "field": "id",
                            "align": "center",
                        },
                    ]

                    squad_table = ui.table(columns=columns, rows=[], row_key="id").classes(
                        "w-full bg-slate-800 text-white"
                    )
                    squad_table.add_slot(
                        "body-cell-action",
                        """
                        <q-td :props="props">
                            <q-btn size="sm" color="negative" label="Sell" @click="$parent.$emit('sell_player', props.value)" />
                        </q-td>
                    """,
                    )

                    def refresh_squad_table():
                        print(state.squad)
                        squad_table.rows = [
                        {
                        
                            "name": p.name,
                            "pos": p.position,
                            "att": p.att,
                            "mid": p.mid,
                            "dfn": p.dfn,
                            "ovr": p.overall,
                            "value": f"€{p.value:,}",
                        }
                        for p in state.squad
                        ]

                    squad_table.on("sell_player", lambda msg: sell_player_handler(msg.args))
                    refresh_squad_table()

            # --- TRANSFER MARKET TAB ---
            with ui.tab_panel(t_market):
                ui.label("Transfer Market").classes(
                    "text-2xl font-bold mb-4 text-amber-400"
                )

                market_table = ui.table(columns=columns, rows=[], row_key="id").classes(
                    "w-full bg-slate-800 text-white"
                )
                market_table.add_slot(
                    "body-cell-action",
                    """
                    <q-td :props="props">
                        <q-btn size="sm" color="positive" label="Buy" @click="$parent.$emit('buy_player', props.value)" />
                    </q-td>
                """,
                )

                def refresh_market_table():
                    market_table.rows = [
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
                        for p in app_state.market_players
                    ]

                market_table.on("buy_player", lambda msg: buy_player_handler(msg.args))

            # --- STANDINGS TAB ---
            with ui.tab_panel(t_standings):
                ui.label("League Table").classes(
                    "text-2xl font-bold mb-4 text-blue-400"
                )

                standings_cols = [
                    {"name": "pos", "label": "Pos", "field": "pos"},
                    {"name": "team", "label": "Team", "field": "team", "align": "left"},
                    {"name": "p", "label": "P", "field": "p"},
                    {"name": "w", "label": "W", "field": "w"},
                    {"name": "d", "label": "D", "field": "d"},
                    {"name": "l", "label": "L", "field": "l"},
                    {"name": "gd", "label": "GD", "field": "gd"},
                    {"name": "pts", "label": "Pts", "field": "pts", "sortable": True},
                ]
                standings_table = ui.table(
                    columns=standings_cols, rows=[], row_key="team"
                ).classes("w-full bg-slate-800 text-white")

                def refresh_standings():
                    sorted_teams = sorted(
                        app_state.teams,
                        key=lambda t: (t.points, t.gd, t.goals_for),
                        reverse=True,
                    )
                    standings_table.rows = [
                        {
                            "pos": idx + 1,
                            "team": t.name,
                            "p": t.played,
                            "w": t.wins,
                            "d": t.draws,
                            "l": t.losses,
                            "gd": t.gd,
                            "pts": t.points,
                        }
                        for idx, t in enumerate(sorted_teams)
                    ]

            # --- FIXTURES TAB ---
            with ui.tab_panel(t_fixtures):
                ui.label("Season Fixtures").classes(
                    "text-2xl font-bold mb-4 text-purple-400"
                )

                fixtures_container = ui.element("div").classes(
                    "w-full space-y-4 max-h-[600px] overflow-y-auto pr-2"
                )

                def refresh_fixtures():
                    fixtures_container.clear()
                    with fixtures_container:
                        for round_idx, round_fixtures in enumerate(app_state.fixtures):
                            with ui.card().classes(
                                "bg-slate-800 border border-slate-700 w-full p-3"
                            ):
                                is_current = round_idx == app_state.current_round
                                title_style = (
                                    "text-emerald-400 font-bold"
                                    if is_current
                                    else "text-slate-400 font-semibold"
                                )
                                ui.label(
                                    f"Round {round_idx + 1} {'(Current)' if is_current else ''}"
                                ).classes(title_style)

                                for f in round_fixtures:
                                    with ui.row().classes(
                                        "w-full justify-between items-center border-t border-slate-700 pt-2 mt-2"
                                    ):
                                        ui.label(f.home.name).classes(
                                            "w-2/5 text-right font-medium"
                                        )
                                        score_str = (
                                            f"{f.home_score} - {f.away_score}"
                                            if f.played
                                            else "vs"
                                        )
                                        score_color = (
                                            "text-amber-400 font-bold"
                                            if f.played
                                            else "text-slate-400"
                                        )
                                        ui.label(score_str).classes(
                                            f"w-1/5 text-center {score_color}"
                                        )
                                        ui.label(f.away.name).classes(
                                            "w-2/5 text-left font-medium"
                                        )

    # --- SIMULATION & DIALOG MODAL MANAGEMENT ---
    match_dialog = ui.dialog().props("persistent")

    def open_match_modal(fixture: Fixture, simulate_mode: bool):
        match_dialog.clear()
        with (
            match_dialog,
            ui.card().classes(
                "w-[500px] bg-slate-900 border border-slate-700 text-white p-6"
            ),
        ):
            ui.label("Match Day Live").classes(
                "text-xl font-bold text-center w-full text-emerald-400 mb-2"
            )

            # Scoreboard
            with ui.row().classes(
                "w-full justify-between items-center bg-slate-800 p-4 rounded-xl mb-4 border border-slate-700"
            ):
                ui.label(fixture.home.name).classes(
                    "w-2/5 text-right text-lg font-bold truncate"
                )
                score_label = ui.label("0 - 0").classes(
                    "w-1/5 text-center text-2xl font-black text-amber-400"
                )
                ui.label(fixture.away.name).classes(
                    "w-2/5 text-left text-lg font-bold truncate"
                )

            # Progress tracker
            timer_label = ui.label("Minute: 0").classes(
                "w-full text-center text-sm font-semibold text-slate-400 mb-1"
            )
            progress_bar = ui.linear_progress(value=0.0).classes("w-full mb-4")

            # Commentary box
            ui.label("Match Events:").classes(
                "text-xs font-bold text-slate-400 uppercase tracking-wider mb-1"
            )
            commentary_scroll = ui.scroll_area().classes(
                "w-full h-40 bg-slate-950 rounded-lg p-3 border border-slate-800 text-sm font-mono mb-4 text-slate-300"
            )

            # Interactive Play buttons
            action_btn_row = ui.row().classes("w-full justify-center")

            match_ctx = {
                "minute": 0,
                "home_score": 0,
                "away_score": 0,
                "is_paused": False,
                "simulated": simulate_mode,
            }

            def append_commentary(text):
                with commentary_scroll:
                    ui.label(text).classes("mb-1 last:font-bold")
                commentary_scroll.scroll_to(percent=1.0)

            def engine_tick():
                if match_ctx["is_paused"]:
                    return

                match_ctx["minute"] += 1
                min_curr = match_ctx["minute"]

                timer_label.set_text(f"Minute: {min_curr}")
                progress_bar.set_value(min_curr / 90.0)

                # Check for scoring chances based on weight differentials
                h_weight = fixture.home.overall
                a_weight = fixture.away.overall
                total = h_weight + a_weight

                                # Base minute factor chance of an action occurring
                if random.random() < 0.06:
                    if random.random() * total < h_weight:
                        # Home chance
                        if random.random() < 0.35: # Conversion efficiency
                            match_ctx['home_score'] += 1
                            score_label.set_text(f"{match_ctx['home_score']} - {match_ctx['away_score']}")
                            append_commentary(f"⚽ {min_curr}' GOAL! {fixture.home.name} scores through a stunning clinical play!")
                        else:
                            append_commentary(f"⚠️ {min_curr}' Chance! {fixture.home.name} shoots wide of the target post.")
                    else:
                        # Away chance
                        if random.random() < 0.35:
                            match_ctx['away_score'] += 1
                            score_label.set_text(f"{match_ctx['home_score']} - {match_ctx['away_score']}")
                            append_commentary(f"⚽ {min_curr}' GOAL! {fixture.away.name} exploits space and strikes it home!")
                        else:
                            append_commentary(f"⚠️ {min_curr}' Near Miss! Great save prevents {fixture.away.name} from scoring.")
                
                # Random flavor events
                elif random.random() < 0.04:
                    events = ["Foul committed in midfield.", "Throw-in processed.", "Yellow card brandished for a rash tackle.", "Corner kick taken and cleared."]
                    append_commentary(f"⏱️ {min_curr}' {random.choice(events)}")

                # Half-Time Break logic
                if min_curr == 45:
                    match_ctx['is_paused'] = True
                    append_commentary("⏸️ HALF TIME! Players head down the tunnel.")
                    with action_btn_row:
                        resume_btn = ui.button('Resume 2nd Half', on_click=lambda: resume_second_half(resume_btn)).props('color=emerald')
                
                # Full-Time logic
                elif min_curr >= 90:
                    match_timer.deactivate()
                    append_commentary("🏁 FULL TIME! The referee blows the final whistle.")
                    finalize_match(fixture, match_ctx['home_score'], match_ctx['away_score'])
                    with action_btn_row:
                        ui.button('Close Dashboard', on_click=match_dialog.close).props('color=slate')



ui.run(title="Alex",port=8000, show=False)
