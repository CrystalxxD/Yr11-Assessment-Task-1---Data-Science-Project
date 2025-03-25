import requests
import difflib
import random
import json
import os

BASE_URL = "https://pokeapi.co/api/v2/"
SEARCH_HISTORY_FILE = "searched_pokemon.json"

def fetch_all_pokemon():
    #Fetches a list of all Pokemon names for error handling.
    url = f"{BASE_URL}pokemon?limit=10000"  # Get all Pokemon
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return [pokemon["name"] for pokemon in data["results"]]
    return []

def suggest_pokemon_name(user_input, pokemon_list):
    """Suggests the closest Pokemon names if user input is incorrect."""
    matches = difflib.get_close_matches(user_input.lower(), pokemon_list, n=5, cutoff=0.5)
    return matches

def get_pokemon_data(pokemon_name):
    #Fetches data from PokeAPI.
    url = f"{BASE_URL}pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None

    data = response.json()
    
    # Basic Info
    name = data["name"].capitalize()
    id_ = data["id"]
    height = data["height"]
    weight = data["weight"]

    # Types
    types = [t["type"]["name"].capitalize() for t in data["types"]]

    # Abilities
    abilities = [a["ability"]["name"].capitalize() for a in data["abilities"]]

    # Base Stats
    stats = {s["stat"]["name"].capitalize(): s["base_stat"] for s in data["stats"]}

    # Held Items
    held_items = [item["item"]["name"].capitalize() for item in data["held_items"]]

    # Moves (Randomly pick 10)
    all_moves = [m["move"]["name"].capitalize() for m in data["moves"]]
    moves = random.sample(all_moves, min(10, len(all_moves)))  # Pick up to 10 moves

    # Evolution Chain
    evolution_chain = get_evolution_chain(data["species"]["url"])

    # Display Results
    print("\n=== Pokemon Information ===")
    print(f"ID: {id_}")
    print(f"Name: {name}")
    print(f"Height: {height}")
    print(f"Weight: {weight}")
    print(f"Types: {', '.join(types)}")
    print(f"Abilities: {', '.join(abilities)}")
    
    print("\n=== Base Stats ===")
    for stat, value in stats.items():
        print(f"{stat}: {value}")
    
    print("\n=== Held Items ===")
    print(", ".join(held_items) if held_items else "None")

    print("\n=== Moves (10 Random Moves) ===")
    print(", ".join(moves) if moves else "None")

    print("\n=== Evolution Chain ===")
    print(" → ".join(evolution_chain) if evolution_chain else "No evolution data.")

    return True 

def get_evolution_chain(species_url):
    #Fetches the Pokemon's evolution chain.
    response = requests.get(species_url)
    if response.status_code != 200:
        return []

    species_data = response.json()
    evolution_url = species_data["evolution_chain"]["url"]
    
    response = requests.get(evolution_url)
    if response.status_code != 200:
        return []

    evolution_data = response.json()
    return extract_evolution_chain(evolution_data["chain"])

def extract_evolution_chain(chain):
    #Extracts Pokemon names from evolution chain data.
    evolution_chain = []
    while chain:
        evolution_chain.append(chain["species"]["name"].capitalize())
        if chain["evolves_to"]:
            chain = chain["evolves_to"][0]
        else:
            break
    return evolution_chain

# Function to load Pokémon search history
def load_search_history():
    if os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

# Function to save searched Pokémon names
def save_search_history(pokemon_name):
    history = load_search_history()
    if pokemon_name.lower() not in history:
        history.append(pokemon_name.lower())
        with open(SEARCH_HISTORY_FILE, "w") as file:
            json.dump(history, file, indent=4)

# Function to find Pokémon with the highest or lowest stats
def find_pokemon_by_stat(stat_name, top_n, highest=True):
    url = f"{BASE_URL}pokemon?limit=1000"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch Pokémon list.")
        return

    all_pokemon = response.json()["results"]
    stat_list = []

    print(f"\nFetching data for {len(all_pokemon)} Pokémon... This might take a while.")

    for pokemon in all_pokemon:
        response = requests.get(pokemon["url"])
        if response.status_code == 200:
            data = response.json()
            stats = {s["stat"]["name"].capitalize(): s["base_stat"] for s in data["stats"]}
            if stat_name in stats:
                stat_list.append((data["name"].capitalize(), stats[stat_name]))

    # Sorting results
    stat_list = sorted(stat_list, key=lambda x: x[1], reverse=highest)
    
    print(f"\nTop {top_n} Pokémon for {stat_name} ({'Highest' if highest else 'Lowest'}):")
    for i, (name, value) in enumerate(stat_list[:top_n], 1):
        print(f"{i}. {name} - {value} {stat_name}")


# Load Pokemon names once
pokemon_list = fetch_all_pokemon()

#loop
while True:
    print("\nWhat would you like to do?")
    print("1. Search for a Pokémon")
    print("2. Find Pokémon with the highest or lowest stats")
    print("3. View search history")
    print("4. Exit")

    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        pokemon_name = input("\nEnter Pokémon name: ").strip()
        
        if pokemon_name.lower() in pokemon_list:
            get_pokemon_data(pokemon_name)
            save_search_history(pokemon_name)
        else:
            suggestions = suggest_pokemon_name(pokemon_name, pokemon_list)
            if suggestions:
                print(f"\nPokémon not found! Did you mean: {', '.join(suggestions)}?")
            else:
                print("\nPokémon not found, and no similar names were found.")

    elif choice == "2":
        valid_stats = ["HP", "Attack", "Defense", "Special-attack", "Special-defense", "Speed"]
        print("\nAvailable stats to search for:")
        print(", ".join(valid_stats))
        
        stat_name = input("Enter a stat (case-sensitive): ").strip()
        if stat_name not in valid_stats:
            print("\nInvalid stat! Please enter one from the list.")
            continue

        top_n = input("Enter how many top Pokémon to display: ").strip()
        if not top_n.isdigit() or int(top_n) <= 0:
            print("\nInvalid number! Please enter a positive integer.")
            continue

        order = input("Find highest or lowest? (h/l): ").strip().lower()
        highest = order == "h"

        find_pokemon_by_stat(stat_name, int(top_n), highest)

    elif choice == "3":
        history = load_search_history()
        if history:
            print("\n=== Search History ===")
            print(", ".join(history))
        else:
            print("\nNo Pokémon have been searched yet.")

    elif choice == "4":
        print("Thank You For Using Pokemon Info Finder")
        break

    else:
        print("\nInvalid choice. Please select a valid option.")
