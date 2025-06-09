import json

def load_history():
    """Load browsing history from a JSON file."""
    try:
        with open('browsing_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(history):
    """Save browsing history to a JSON file."""
    with open('browsing_history.json', 'w') as f:
        json.dump(history, f, indent=2)