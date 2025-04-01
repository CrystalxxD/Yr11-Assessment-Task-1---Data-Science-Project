import requests
import difflib
import random
import json
import os
import asyncio
import aiohttp

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
    evolution_chain = get_evolution_chain(data["species"]["url"], pokemon_name.lower())

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

def get_evolution_chain(species_url, target_pokemon):  
    response = requests.get(species_url)
    if response.status_code != 200:
        return []

    species_data = response.json()
    evolution_url = species_data["evolution_chain"]["url"]
    
    response = requests.get(evolution_url)
    if response.status_code != 200:
        return []

    evolution_data = response.json()
    return format_evolution_chain(evolution_data["chain"], target_pokemon) 

def format_evolution_chain(chain, target_pokemon): 
    path = []
    
    def traverse(chain, current_path):
        current_name = chain["species"]["name"].lower()
        new_path = current_path + [current_name.capitalize()]
        
        if current_name == target_pokemon.lower():
            return new_path
        
        for evolution in chain["evolves_to"]:
            result = traverse(evolution, new_path)
            if result:
                return result
        
        return None
    
    final_path = traverse(chain, [])
    return final_path if final_path else [target_pokemon.capitalize()]

# Function to load Pokemon search history
def load_search_history():
    if os.path.exists(SEARCH_HISTORY_FILE):
        with open(SEARCH_HISTORY_FILE, "r") as file:
            return json.load(file)
    return []

# Function to save searched Pokemon names
def save_search_history(pokemon_name):
    history = load_search_history()
    if pokemon_name.lower() not in history:
        history.append(pokemon_name.lower())
        with open(SEARCH_HISTORY_FILE, "w") as file:
            json.dump(history, file, indent=4)

def clear_search_history():
    #Deletes all Pokemon search history from the JSON file.
    if os.path.exists(SEARCH_HISTORY_FILE):
        os.remove(SEARCH_HISTORY_FILE)
        print("\nSearch history has been cleared successfully.")
    else:
        print("\nNo search history file found. Nothing to delete.")

# Function to find Pokemon with the highest or lowest stats 
#async for it to call Pokemon Faster
async def fetch_pokemon_data(session, url):
    """Fetches Pokemon data asynchronously."""
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
    return None

async def find_pokemon_by_stat(stat_name, pokemon_amount, highest=True):
    stat_name = stat_name.lower() 
    
    url = f"{BASE_URL}pokemon?limit=10000"
    
    async with aiohttp.ClientSession() as session:
        response = await fetch_pokemon_data(session, url)
        
        if not response:
            print("Failed to fetch Pokemon list.")
            return

        all_pokemon = response["results"]
        stat_list = []

        print(f"\nFetching data for {len(all_pokemon)} Pokemon... This might take a while.")

        tasks = [fetch_pokemon_data(session, pokemon["url"]) for pokemon in all_pokemon]
        results = await asyncio.gather(*tasks)

        for data in results:
            if data:
                stats = {s["stat"]["name"].lower(): s["base_stat"] for s in data["stats"]}
                if stat_name in stats:
                    stat_list.append((data["name"].capitalize(), stats[stat_name]))

        stat_list = sorted(stat_list, key=lambda x: x[1], reverse=highest)

        print(f"\nTop {pokemon_amount} Pokemon for {stat_name.capitalize()} ({'Highest' if highest else 'Lowest'}):")
        for i, (name, value) in enumerate(stat_list[:pokemon_amount], 1):
            print(f"{i}. {name} - {value} {stat_name.capitalize()}")

# Load Pokemon names once
pokemon_list = fetch_all_pokemon()

#loop
def main():
    while True:
        print("\nWhat would you like to do?")
        print("1. Search for a Pokemon")
        print("2. Find Pokemon with the highest or lowest stats")
        print("3. View search history")
        print("4. Clear search history")
        print("5. Exit")

        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        if choice == "1":
            pokemon_name = input("\nEnter Pokemon name: ").strip()
            
            if pokemon_name.lower() in pokemon_list:
                get_pokemon_data(pokemon_name)
                save_search_history(pokemon_name)
            else:
                suggestions = suggest_pokemon_name(pokemon_name, pokemon_list)
                if suggestions:
                    print(f"\nPokemon not found! Did you mean: {', '.join(suggestions)}?")
                else:
                    print("\nPokemon not found, and no similar names were found.")

        elif choice == "2":
            valid_stats = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
            print("\nAvailable stats to search for:")
            print(", ".join(valid_stats))

            stat_name = input("Enter a stat: ").strip().lower()  # Convert to lowercase
            if stat_name not in valid_stats:
                print("\nInvalid stat! Please enter one from the list.")
                continue

            pokemon_amount = input("Enter how many top Pokemon to display: ").strip()
            if not pokemon_amount.isdigit() or int(pokemon_amount) <= 0:
                print("\nInvalid number! Please enter a positive integer.")
                continue

            order = input("Find highest or lowest? (h/l): ").strip().lower()
            highest = order == "h"

            asyncio.run(find_pokemon_by_stat(stat_name, int(pokemon_amount), highest))  # Run async function properly

        elif choice == "3":
            history = load_search_history()
            if history:
                print("\n=== Search History ===")
                print(", ".join(history))
            else:   
                print("\nNo Pokemon have been searched yet.")
      
        elif choice == "4":
            clear_search_history()

        elif choice == "5":
            print("Thank You For Using Pokemon Info Finder")
            break

        else:
            print("\nInvalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()