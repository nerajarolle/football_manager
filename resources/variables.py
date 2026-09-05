# --- VARIABLES AND DEFAULTS---

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

SERIE_TEAMS = [
    "Atalanta",
    "Bologna",
    "Cagliari",
    "Como",
    "Empoli",
    "Fiorentina",
    "Genoa",
    "Hellas Verona",
    "Inter",
    "Juventus",
    "Lazio",
    "Lecce",
    "Milan",
    "Monza",
    "Napoli",
    "Parma",
    "Roma",
    "Torino",
    "Udinese",
    "Venezia",
    "Bari",
    "Brescia",
    "Cesena",
    "Frosinone",
    "Palermo",
    "Sampdoria",
    "Sassuolo",
    "Spezia",
    "Südtirol",
    "Catanzaro",
]

TAB_PANEL_HEADER_LABEL_CLASSES = "text-2xl font-bold mb-4 text-emerald-400"
TEAM_SQUAD_PANEL_ROW_CLASSES = (
    "w-full justify-between items-center bg-slate-800 p-4"
    " rounded-lg mb-4 border border-slate-700"
)

TEAM_SQUAD_PANEL_PLAYER_TABLE_COLUMNS = [
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

LOGO_COLORS = [
    ("#1f6b58", "#c9f26b"),
    ("#ef7459", "#18221f"),
    ("#3467a5", "#f4f1e9"),
    ("#8a4d76", "#f6c85f"),
    ("#c56b2f", "#f4f1e9"),
    ("#3c8c91", "#18221f"),
    ("#6c4e9b", "#f4f1e9"),
    ("#a33b4b", "#f6c85f"),
    ("#2e5d34", "#f4f1e9"),
    ("#d96c2a", "#18221f"),
]

PLAYER_SKILLS = [
    "shooting",
    "passing",
    "dribbling",
    "stamina",
    "tackle",
    "speed",
    "vision",
    "crossing",
    "positioning",
    "marking",
    "reflexes",
    "handling",
    "strength",
]
