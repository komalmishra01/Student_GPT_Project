# data_manager.py
import json
import os
from typing import Dict, List, Tuple

HISTORY_FILE = "chat_history.json"

def load_history() -> Dict[str, List[Tuple[str, str]]]:
    """Chat history ko JSON file se load karta hai."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                # JSON dictionary load karein
                data = json.load(f)
                
                # History ko Tuple format mein convert karein
                processed_data = {}
                for key, history_list in data.items():
                    processed_data[key] = [tuple(item) for item in history_list]
                
                return processed_data
        except json.JSONDecodeError:
            print("Warning: chat_history.json is corrupt. Starting with empty history.")
            return {}
    return {}

def save_history(history: Dict[str, List[Tuple[str, str]]]):
    """Chat history ko JSON file mein save karta hai."""
    try:
        # Tuple ko list mein convert karein taki woh JSON serializable ho
        serializable_history = {}
        for key, history_list in history.items():
            serializable_history[key] = [list(item) for item in history_list]
            
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_history, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")

# Initial history load karo taki app shuru hote hi data available ho
CHAT_HISTORY = load_history()