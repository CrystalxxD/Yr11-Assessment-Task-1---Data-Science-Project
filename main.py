import requests
import difflib
import random

BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

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

# Load Pokemon names once
pokemon_list = fetch_all_pokemon()

#loop
while True:
    pokemon_name = input("\nEnter Pokemon name (or type 'exit' to quit): ").strip()
    
    if pokemon_name.lower() == "exit":
        print("Thank You for using Pokemon Info Finder")
        break

    if pokemon_name.lower() in pokemon_list:
        get_pokemon_data(pokemon_name)
    else:
        suggestions = suggest_pokemon_name(pokemon_name, pokemon_list)
        if suggestions:
            print(f"\nPokemon not found! Did you mean: {', '.join(suggestions)}?")
        else:
            print("\nPokemon not found, and no similar names were found.")
