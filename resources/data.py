from secrets import choice

from resources.helpers import get_round_fixture
from resources.objects import Fixture, Player, Team
from resources.variables import DEFAULT_TEAMS


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
        self.teams = {}  # name -> Team
        self.fixtures: list[Fixture] = []
        self.current_fixture_idx = 0
        self.season_over = False
        self.rounds = 0

    def _process_all_team_names(self, all_team_names):
        if self.team_name not in all_team_names:
            all_team_names[0] = self.team_name  # Replace first if custom
        else:
            all_team_names.remove(self.team_name)
            all_team_names.insert(0, self.team_name)
    
    def _generate_market(self):
        # Generate transfer market for the season
        if not self.transfer_list:
            for i in range(10):
                player = Player(position=choice(["GK", "DEF", "MID", "ATT"]))  # Get a random player
                if player.name not in [p.name for p in self.transfer_list]:  # Avoid duplicates
                    self.transfer_list.append(player)

    def init_season(self, user_team_name):
        # pylint:disable=too-many-locals, attribute-defined-outside-init
        self.team_name = user_team_name
        self.team = Team(name=user_team_name, is_user=True)
        self.budget = 25000000
        self.squad = self.team.squad
        self.season_over = False
        self.current_fixture_idx = 0

        # Populate league teams
        all_team_names = list(DEFAULT_TEAMS)
        self._process_all_team_names(all_team_names)
        
        self.teams: dict[str, Team] = {}
        for t in all_team_names:
            team = Team(name=t, is_user=(t == self.team_name))
            self.teams[t] = team

        # Generate Double Round-Robin fixtures
        self.fixtures = []
        team_list = list(self.teams.keys())
        # Simple round-robin scheduling
        n = len(team_list)
        rounds: list[list[tuple[int, Team, Team]]] = []
        for r in range(n - 1):
            round_fixtures = get_round_fixture(team_list=team_list, r=r)
            team_list.insert(1, team_list.pop())
            rounds.append(round_fixtures)

        
        for rnd in rounds:
            for r, h, a in rnd:
                self.fixtures.append(
                    Fixture(home=h, away=a, r=r)
                )
                # Second half (reverse fixtures)
        #second_half = []
        # for rnd in rounds:
        #     rnd_rev = []
        #     for r, h, a in rnd:
        #         rnd_rev.append((r, a, h))
        #     second_half.append(rnd_rev)
        for rnd in rounds:
            for r, h, a in rnd:
                self.fixtures.append(Fixture(home=a, away=h, r=r+n-1))
                
        self.rounds = len(rounds) * 2

        self._generate_market()  # Generate transfer market for the season
        print(f"Season initialized for team '{self.team_name}' with {len(self.fixtures)} fixtures.")
        print(f"Transfer market has {len(self.transfer_list)} players available.")