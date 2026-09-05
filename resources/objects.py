from dataclasses import dataclass
from random import randint
from secrets import choice
import uuid

from resources.variables import FIRST_NAMES, LAST_NAMES, PLAYER_SKILLS, POSITIONS

class Player:
    def __init__(
        self,
        position: str | None = None,
        age: int | None = None,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.position = position or choice(POSITIONS)
        self.age = age if age is not None else randint(18, 32)
        self.physical = randint(52, 84)
        self.mental = randint(50, 86)
        self.name = f"{choice(FIRST_NAMES)} {choice(LAST_NAMES)}"
        self.shooting = randint(35, 90)
        self.passing = randint(35, 90)
        self.dribbling = randint(35, 92)
        self.stamina = randint(45, 92)
        self.tackle = randint(30, 90)
        self.speed = randint(40, 94)
        self.vision = randint(35, 90)
        self.crossing = randint(35, 90)
        self.positioning = randint(35, 90)
        self.marking = randint(30, 90)
        self.reflexes = randint(35, 90)
        self.handling = randint(35, 90)
        self.strength = randint(35, 90)
        self.potential = randint(55, 92)
        self.value = randint(8, 28) * 100000
        self.wage = randint(12, 45) * 1000
        self.stats = {"appearances": 0, "goals": 0, "assists": 0, "form": 6.5}

        if position == "GK":
            self.shooting = randint(18, 42)
            self.passing = randint(52, 82)
            self.speed = randint(44, 78)
            self.tackle = randint(58, 86)
            self.stamina = randint(58, 85)
        elif position in {"CB", "LB", "RB", "DM"}:
            self.tackle = randint(60, 90)
            self.marking = randint(55, 90)
            self.speed = randint(55, 88)
            self.stamina = randint(60, 90)
        elif position in {"CM", "AM"}:
            self.passing = randint(60, 90)
            self.dribbling = randint(50, 90)
            self.shooting = randint(45, 85)
            self.crossing = randint(50, 90)
        elif position in {"LW", "RW", "ST"}:
            self.shooting = randint(55, 92)
            self.speed = randint(60, 96)
            self.dribbling = randint(55, 92)
        self.att = round((self.shooting + self.dribbling + self.speed) / 3)
        self.mid = round((self.passing + self.dribbling + self.stamina + self.vision + self.crossing) / 5)
        self.dfn = round((self.tackle + self.stamina + self.speed + self.marking) / 4)
        self.gk = round((self.reflexes + self.handling + self.positioning) / 3)
        self.overall = self.recalculate_overall()

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "age": self.age,
            "physical": self.physical,
            "mental": self.mental,
            "shooting": self.shooting,
            "passing": self.passing,
            "dribbling": self.dribbling,
            "stamina": self.stamina,
            "tackle": self.tackle,
            "speed": self.speed,
            "vision": self.vision,
            "crossing": self.crossing,
            "positioning": self.positioning,
            "marking": self.marking,
            "reflexes": self.reflexes,
            "handling": self.handling,
            "strength": self.strength,
            "potential": self.potential,
            "value": self.value,
            "wage": self.wage,
            "stats": self.stats,
            "att": self.att,
            "mid": self.mid,
            "dfn": self.dfn,
            "gk": self.gk,
            "overall": self.overall
        }

    def recalculate_overall(self) -> int:
        skills = [getattr(self, skill) for skill in PLAYER_SKILLS]
        return round(sum(skills) / len(skills))


class PlayerOld(dict):
    def __init__(self, name: str, position: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.position = position  # 'ATT', 'MID', 'DEF'
 
        # Genera attributi casuali basati sulla posizione
        if position == 'ATT':
            self.att = randint(70, 95)
            self.mid = randint(50, 75)
            self.dfn = randint(30, 55)
        elif position == 'MID':
            self.att = randint(60, 85)
            self.mid = randint(70, 95)
            self.dfn = randint(60, 85)
        else: # DEF
            self.att = randint(30, 55)
            self.mid = randint(50, 75)
            self.dfn = randint(70, 95)

        self.overall = round((self.att + self.mid + self.dfn) / 3)
        self.value = self.overall * randint(250_000, 400_000)

class Team:
    def __init__(self, name: str, is_user: bool = False):
        self.id = str(uuid.uuid4())
        self.name = name
        self.is_user = is_user
        self.budget = 20_000_000 if is_user else randint(2_000_000, 60_000_000)
        self.players: list[Player] = []

        self.played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0
        self.gd = 0
        self.points = 0
        self.generate_squad()
    
    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_user": self.is_user,
            "budget": self.budget,
            "players": [vars(p) for p in self.players],
            "played": self.played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "gd": self.gd,
            "points": self.points
        }
        

    # def _generate_initial_squad(self):
    #     positions = ['GOL'] * 2 + ['ATT'] * 4 + ['MID'] * 6 + ['DEF'] * 5
    #     for pos in positions:
    #         #full_name = f"{choice(FIRST_NAMES)} {choice(LAST_NAMES)}"
    #         self.players.append(Player(pos))

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
        dfn_players = [p.dfn for p in self.players if p.position in ['DEF','GOL'] ]
        return round(sum(dfn_players) / len(dfn_players)) if dfn_players else 50

    @property
    def overall(self) -> int:
        return round((self.att + self.mid + self.dfn) / 3)
    
    @property
    def squad(self) -> list[Player]:
        return self.players
    
    def generate_squad(self):
        players = []
        # 2 GKs, 6 DEFs, 6 MIDs, 4 ATTs = 18 players
        for _ in range(3):
            players.append(Player("GK"))
        for _ in range(6):
            players.append(Player("DEF"))
        for _ in range(6):
            players.append(Player("MID"))
        for _ in range(4):
            players.append(Player("ATT"))
        self.players = players    

class Fixture: # pylint: disable=all
    def __init__(self, home: Team, away: Team, r: int):
        self.id = str(uuid.uuid4())
        self.home = home
        self.away = away
        self.round = r
        self.home_score = 0
        self.away_score = 0
        self.home_scorers = []
        self.away_scorers = []
        self.played = False
        self.stats = {
            "home_possession": 0,
            "away_possession": 0,
            "home_shots": 0,
            "away_shots": 0
        }
    
    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "home": self.home.name,
            "away": self.away.name,
            "round": self.round,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "home_scorers": self.home_scorers,
            "away_scorers": self.away_scorers,
            "played": self.played,
            "stats": self.stats
        }
