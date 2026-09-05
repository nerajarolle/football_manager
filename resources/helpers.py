
from random import randint
from secrets import choice

from resources.objects import Fixture, Player, Team
from resources.variables import LOGO_COLORS


# def generate_team_squad() -> list[Player]:
#     squad = []
#     # 2 GKs, 6 DEFs, 6 MIDs, 4 ATTs = 18 players
#     for _ in range(3):
#         squad.append(Player("GK"))
#     for _ in range(6):
#         squad.append(Player("DEF"))
#     for _ in range(6):
#         squad.append(Player("MID"))
#     for _ in range(4):
#         squad.append(Player("ATT"))
#     return squad

def get_chance_for_event(fixture: Fixture) -> str:
    #print(f"Simulating event for fixture: {fixture.home.name} vs {fixture.away.name}")
    overall1 = fixture.home.overall
    overall2 = fixture.away.overall
    team_diff = abs(overall1 - overall2)
    chance1 = overall1 / (overall1 + overall2)
    _chance2 = overall2 / (overall1 + overall2)
    roll = randint(0, 100) / 100
    #print(f"Roll: {roll}, Team Diff: {team_diff}, Chance1: {chance1}")
    is_a_goal = roll + team_diff * 0.001 > 0.95
    if is_a_goal:
        if randint(1, 100) <= chance1 * 100:
            #print(f"Goal for {fixture.home.name}")
            fixture.home_score += 1
            fixture.stats["home_shots"] += 1
            scorer = get_scorer(fixture.home)
            scorer.stats["goals"] += 1
            fixture.home_scorers.append(scorer.name)
            return f"Goal for {fixture.home.name}! Scored by {scorer.name}"
        fixture.away_score += 1
        print(f"Goal for {fixture.away.name}")
        fixture.stats["away_shots"] += 1
        scorer = get_scorer(fixture.away)
        scorer.stats["goals"] += 1
        fixture.away_scorers.append(scorer.name)
        return f"Goal for {fixture.away.name}! Scored by {scorer.name}"
    is_a_chance = roll + team_diff * 0.001 > 0.82
    if is_a_chance:
        if randint(1, 100) <= chance1 * 100:
            fixture.stats["home_shots"] += 1
            return get_chance(fixture.home.name)
        fixture.stats["away_shots"] += 1
        return get_chance(fixture.away.name)
    is_event = roll + team_diff * 0.001 > 0.76
    if is_event:
        if randint(1, 100) <= chance1 * 100:
            fixture.stats["home_shots"] += 1
            player = choice(fixture.home.players)
            return get_action_commentary(player, fixture.home.name)
        fixture.stats["away_shots"] += 1
        player = choice(fixture.away.players)
        return get_action_commentary(player, fixture.away.name)
    return ""


def get_scorer(team: Team) -> Player:
    r = randint(1, 100)
    defender_goal = r <= 10  # 10% chance for a defender to score
    midfielder_goal = r <= 40  # 40% chance for a midfielder to score
    if defender_goal:
        scorer = choice([player for player in team.players if player.position == "DEF"])
    elif midfielder_goal:
        scorer = choice([player for player in team.players if player.position == "MID"])
    else:
        scorer = choice([player for player in team.players if player.position in ["ATT"]])
    return scorer

def get_action_commentary(player: Player, team: str) -> str:
    actions = {
        "GK": ["claims the cross calmly", "launches a quick counter-attack", "makes a sharp save"],
        "CB": ["wins a strong challenge", "steps in to break up the move", "heads the ball clear"],
        "LB": ["overlaps down the left flank", "puts in a dangerous cross", "tracks back to stop the attack"],
        "RB": ["drives forward on the right", "whips a cross into the box", "closes down the winger"],
        "DM": ["breaks up the midfield move", "recovers possession intelligently", "switches play with a fine pass"],
        "CM": ["threads a pass through midfield", "keeps the tempo moving", "arrives late in the box"],
        "AM": ["slips a clever pass through", "creates space between the lines", "tests the keeper from distance"],
        "LW": ["cuts inside from the left", "takes on the full-back", "sends a low ball across goal"],
        "RW": ["beats the defender on the right", "drives into the penalty area", "delivers a teasing cross"],
        "ST": ["holds up play under pressure", "gets onto the end of a through ball", "forces the defence into a mistake"]
    }
    options = actions.get(player.position, ["moves the ball forward"])
    return f"{player.name} {choice(options)} for {team}."

def get_chance(team: str) -> str:
    options = [
        f"{team} work an opening on the edge of the box.",
        f"{team} break quickly and threaten behind the defence.",
        f"{team} swing a dangerous ball into the area.",
        f"{team} test the goalkeeper with a low effort."
    ]
    return choice(options)



def get_round_fixture(
    team_list: list[str], r: int, teams: dict[str, Team] | None = None
) -> list[tuple[int, Team, Team]]:
    n = len(team_list)
    round_fixtures: list[tuple[int, Team, Team]] = []
    for i in range(n // 2):
        t1 = team_list[i]
        t2 = team_list[n - 1 - i]
        if i == 0 and r % 2 == 1:
            home_name, away_name = t2, t1
        else:
            home_name, away_name = t1, t2
        if teams is None:
            teams = {name: Team(name) for name in team_list}
        round_fixtures.append((r, teams[home_name], teams[away_name]))
    return round_fixtures

def normalize_player_price(price: str) -> int:
    return int(price.removeprefix("€").replace(",",""))

def get_other_teams(teams: dict) -> list[Team]:
    return [team for _k, team in teams.items()]


def get_transfer_buyers(teams: dict[str, Team], seller_name: str, player: Player) -> list[Team]:
    minimum_offer = int(player.value * 85 / 100)
    return [
        team
        for team in teams.values()
        if team.name != seller_name
        and team.budget >= minimum_offer
        and abs(team.overall - player.overall) <= 5
    ]


def get_transfer_offer(buyer: Team, player: Player) -> tuple[int, int]:
    offer = min(
        buyer.budget,
        randint(int(player.value * 85 / 100), int(player.value * 110 / 100)),
    )
    maximum_offer = min(buyer.budget, int(player.value * 125 / 100))
    return offer, maximum_offer


def complete_transfer(seller: Team, buyer: Team, player: Player, price: int) -> bool:
    if player not in seller.players or buyer.budget < price or price <= 0:
        return False
    seller.players.remove(player)
    buyer.players.append(player)
    buyer.budget -= price
    return True


def get_market_players(
    teams: dict[str, Team], free_agents: list[Player], buyer_name: str
) -> list[tuple[Player, Team | None]]:
    market_players: list[tuple[Player, Team | None]] = [
        (player, None) for player in free_agents
    ]
    for team in teams.values():
        if team.name != buyer_name:
            market_players.extend((player, team) for player in team.players)
    return market_players


def complete_market_purchase(
    buyer: Team,
    seller: Team | None,
    free_agents: list[Player],
    player: Player,
    price: int,
) -> bool:
    if price < 0:
        return False
    if seller is None:
        if player not in free_agents:
            return False
        free_agents.remove(player)
    elif not complete_transfer(seller, buyer, player, price):
        return False
    if seller is None:
        buyer.players.append(player)
    else:
        seller.budget += price
    return True


def update_fixture_stats(fixture: Fixture, teams: dict[str, Team]) -> None:
    fixture.played = True
    for team in (fixture.home, fixture.away):
        team_data = teams[team.name]
        team_data.played += 1
        if team == fixture.home:
            team_data.goals_for += fixture.home_score
            team_data.goals_against += fixture.away_score
        else:
            team_data.goals_for += fixture.away_score
            team_data.goals_against += fixture.home_score

        if fixture.home_score > fixture.away_score:
            if team == fixture.home:
                team_data.wins += 1
                team_data.points += 3
            else:
                team_data.losses += 1
        elif fixture.home_score < fixture.away_score:
            if team == fixture.away:
                team_data.wins += 1
                team_data.points += 3
            else:
                team_data.losses += 1
        else:
            team_data.draws += 1
            team_data.points += 1
# def simulate_match(fixture):
#     # Simulate match logic here
#     fixture.home_score = randint(0, 5)
#     fixture.away_score = randint(0, 5)
#     fixture.home_scorers = [get_scorer(fixture.home).name for _ in range(fixture.home_score)]
#     fixture.away_scorers = [get_scorer(fixture.away).name for _ in range(fixture.away_score)]
#     fixture.played = True


# def normalize_player(raw: dict) -> dict:
#     if not isinstance(raw, dict):
#         return raw
#     normalized = dict(raw)
#     scores = {
#         "physical": normalized.get("physical", randint(52, 84)),
#         "mental": normalized.get("mental", randint(50, 86)),
#         "shooting": normalized.get("shooting", randint(35, 90)),
#         "passing": normalized.get("passing", randint(35, 90)),
#         "dribbling": normalized.get("dribbling", randint(35, 92)),
#         "stamina": normalized.get("stamina", randint(45, 92)),
#         "tackle": normalized.get("tackle", randint(30, 90)),
#         "speed": normalized.get("speed", randint(40, 94)),
#         "vision": normalized.get("vision", randint(35, 90)),
#         "crossing": normalized.get("crossing", randint(35, 90)),
#         "positioning": normalized.get("positioning", randint(35, 90)),
#         "marking": normalized.get("marking", randint(30, 90)),
#         "reflexes": normalized.get("reflexes", randint(35, 90)),
#         "handling": normalized.get("handling", randint(35, 90)),
#         "strength": normalized.get("strength", randint(35, 90)),
#     }
#     for key, value in scores.items():
#         normalized[key] = value
#     stats = dict(normalized.get("stats") or {})
#     normalized["stats"] = {
#         "appearances": int(stats.get("appearances", 0)),
#         "goals": int(stats.get("goals", 0)),
#         "assists": int(stats.get("assists", 0)),
#         "form": float(stats.get("form", 6.5)),
#     }
#     normalized["overall"] = int(normalized.get("overall") or recalculate_player_overall(normalized))
#     normalized["potential"] = int(normalized.get("potential", randint(55, 92)))
#     normalized["value"] = int(normalized.get("value", randint(8, 28) * 100000))
#     normalized["wage"] = int(normalized.get("wage", randint(12, 45) * 1000))
#     normalized.setdefault("id", str(uuid4()))
#     normalized.setdefault("name", "Player")
#     normalized.setdefault("position", choice(POSITIONS))
#     normalized.setdefault("age", randint(18, 32))
#     return normalized

def make_logo(team: str, index: int) -> dict[str, str]:
    words = [word for word in team.split() if word]
    initials = "".join(word[0] for word in words[:2]).upper() or team[:2].upper()
    primary, accent = LOGO_COLORS[index % len(LOGO_COLORS)]
    return {"initials": initials, "primary": primary, "accent": accent}


# def make_team_logos(team_name: str) -> dict[str, dict[str, str]]:
#     return {
#         team: make_logo(team, index)
#         for index, team in enumerate([team_name, *OPPONENTS])
#     }

