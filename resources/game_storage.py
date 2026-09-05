from nicegui import ui, app
from resources.data import GameState


def save_to_browser(state: GameState):
    try:
        app.storage.user.clear()
        app.storage.user.update({"football-save": state})
        ui.notify("Game saved successfully!", type="positive")
    except Exception as e:
        ui.notify(f"Error saving game: {e}", type="negative")


def load_from_browser(_state: GameState) -> bool:
    try:
        loaded_game = app.storage.user.get("football-save")
        if loaded_game is None:
            ui.notify("No savegame found!")
            return False
        ui.notify("Game loaded successfully!", type="positive")
        return True
    except Exception as e:
        ui.notify(f"Error loading game: {e}", type="negative")
        return False
