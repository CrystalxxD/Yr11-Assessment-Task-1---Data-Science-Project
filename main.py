import requests  # For sending HTTP requests 
import difflib  # For finding close matches between strings
import random  # For selecting random items
import json  # For working with JSON data
import os  # For interacting with the file system
import asyncio  # For asynchronous programming
import aiohttp  # For asynchronous HTTP requests

BASE_URL = "https://pokeapi.co/api/v2/"  # URL for Poke API
SEARCH_HISTORY_FILE = "searched_pokemon.json"  # File name for storing previously searched Pokemon

def fetch_all_pokemon():
    # Fetches a list of all Pokemon names for error handling.
    url = f"{BASE_URL}pokemon?limit=10000"  # Get all Pokemon
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json() 
        return [pokemon["name"] for pokemon in data["results"]]
    return []

def suggest_pokemon_name(user_input, pokemon_list):
    # Suggests the closest Pokemon names if user input is incorrect.
    matches = difflib.get_close_matches(user_input.lower(), pokemon_list, n=5, cutoff=0.5)  # Finds close matches
    return matches

def get_pokemon_data(pokemon_name):
    # Fetches data about a specific Pokemon from the PokeAPI
    url = f"{BASE_URL}pokemon/{pokemon_name.lower()}"  # URL for the specific Pokemon
    response = requests.get(url)
    
    if response.status_code != 200:
        return None

    data = response.json()
    
    # Basic Info
    name = data["name"].capitalize()  # Pokemon name Capitalized
    id_ = data["id"]  # Pokemon ID
    height = data["height"]  # Height of Pokemon
    weight = data["weight"]  # Weight of Pokemon

    # Types
    types = [t["type"]["name"].capitalize() for t in data["types"]]  # Extracts and capitalizes types

    # Abilities
    abilities = [a["ability"]["name"].capitalize() for a in data["abilities"]]  # Extracts and capitalizes abilities

    # Base Stats
    stats = {s["stat"]["name"].capitalize(): s["base_stat"] for s in data["stats"]}  # Extracts and capitalizes stats

    # Held Items
    held_items = [item["item"]["name"].capitalize() for item in data["held_items"]]  # Extracts and capitalizes held items

    # Moves (Randomly pick 10)
    all_moves = [m["move"]["name"].capitalize() for m in data["moves"]]
    moves = random.sample(all_moves, min(10, len(all_moves)))  # Pick up to 10 moves

    # Evolution Chain
    evolution_chain = get_evolution_chain(data["species"]["url"], pokemon_name.lower())  # Extracts and capitalizes the whole evolution chain

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
    # Fetches evolution data and formats it
    response = requests.get(species_url)
    if response.status_code != 200:
        return []

    species_data = response.json()  # Converts the response to JSON
    evolution_url = species_data["evolution_chain"]["url"]  # Extracts the evolution chain URL
    
    response = requests.get(evolution_url)  # Sends an HTTP GET request for the evolution chain
    if response.status_code != 200:
        return []

    evolution_data = response.json()
    return format_evolution_chain(evolution_data["chain"], target_pokemon)  # Formats the evolution chain

def format_evolution_chain(chain, target_pokemon): 
    # Formats the evolution chain into a readable format.
    path = []
    
    def traverse(chain, current_path):
        current_name = chain["species"]["name"].lower()  # Extracts the species name
        new_path = current_path + [current_name.capitalize()]  # Adds the current name to the path
        
        if current_name == target_pokemon.lower():  # Checks if the target Pokemon is found
            return new_path
        
        for evolution in chain["evolves_to"]:  # Goes through all possible evolutions for specified pokemon
            result = traverse(evolution, new_path)
            if result:
                return result
        
        return None
    
    final_path = traverse(chain, [])
    return final_path if final_path else [target_pokemon.capitalize()]  # Returns the final path or the target name

def load_search_history(): 
    # Function to load previously searched Pokemon names
    if os.path.exists(SEARCH_HISTORY_FILE):  # Checks if the file exists
        with open(SEARCH_HISTORY_FILE, "r") as file:  # Opens file in read mode
            return json.load(file)
    return []

def save_search_history(pokemon_name): 
    # Function to save searched Pokemon names
    history = load_search_history()  # Loads the current history
    if pokemon_name.lower() not in history:  # Checks if the name is not already in history
        history.append(pokemon_name.lower())  # Appends the name to the history
        with open(SEARCH_HISTORY_FILE, "w") as file:  # Opens the file in write mode
            json.dump(history, file, indent=4)

def clear_search_history():
    # Function to clear all Pokemon search history from the JSON file. 
    if os.path.exists(SEARCH_HISTORY_FILE):
        os.remove(SEARCH_HISTORY_FILE)  # Removes the search history file
        print("\nSearch history has been cleared successfully.")
    else:
        print("\nNo search history file found. Nothing to delete.")

async def fetch_pokemon_data(session, url):
    # Fetches Pokemon data asynchronously.
    async with session.get(url) as response:  # Sends an asynchronous get HTTP request
        if response.status == 200:
            return await response.json()
    return None

async def find_pokemon_by_stat(stat_name, pokemon_amount, highest=True):
    # Finds Pokemon with the highest or lowest value for a specific stat.
    stat_name = stat_name.lower()  # Changes stat_name to be lowercase
    
    url = f"{BASE_URL}pokemon?limit=10000"
    
    async with aiohttp.ClientSession() as session:  # Creates an asynchronous HTTP session
        response = await fetch_pokemon_data(session, url)  # Fetches the list of all Pokemon
        
        if not response:
            print("Failed to fetch Pokemon list.") 
            return

        all_pokemon = response["results"]
        stat_list = []

        print(f"\nFetching data for {len(all_pokemon)} Pokemon... This might take a while.")

        tasks = [fetch_pokemon_data(session, pokemon["url"]) for pokemon in all_pokemon]  # Creates tasks for fetching Pokemon data
        results = await asyncio.gather(*tasks)

        for data in results:
            if data:
                stats = {s["stat"]["name"].lower(): s["base_stat"] for s in data["stats"]}  # Create a dictionary of the Pokemon's stats
                if stat_name in stats:
                    stat_list.append((data["name"].capitalize(), stats[stat_name]))  # Capitalizes the name for display and gets the base_stat value

        stat_list = sorted(stat_list, key=lambda x: x[1], reverse=highest)  # Sort the list of Pokemon based on the specified stat and checks if the user wanted it by highest or by lowest.

        print(f"\nTop {pokemon_amount} Pokemon for {stat_name.capitalize()} ({'Highest' if highest else 'Lowest'}):")  # Displays the top Pokemon based on the selected stat
        for i, (name, value) in enumerate(stat_list[:pokemon_amount], 1):  # Loops through the sorted list and prints the Pokemon name and their stat value
            print(f"{i}. {name} - {value} {stat_name.capitalize()}")  

pokemon_list = fetch_all_pokemon()  # Load Pokemon names once

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
            while True:  # Loop until valid input is received
                pokemon_name = input("\nEnter Pokemon name: ").strip()
            
                if pokemon_name.lower() in pokemon_list:
                    get_pokemon_data(pokemon_name)
                    save_search_history(pokemon_name)
                    break  # Exit loop if valid Pokemon name is entered
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

            while True:  # Loop until valid stat input is received
                stat_name = input("Enter a stat: ").strip().lower()  # Convert to lowercase
                if stat_name not in valid_stats:
                    print("\nInvalid stat! Please enter one from the list.")
                    continue  # Keep asking if invalid stat
                break  # Exit loop if valid stat is entered

            while True:  # Loop until valid number input is received
                pokemon_amount = input("Enter how many top Pokemon to display (maximum amount of pokemon is 1302): ").strip()
                if not pokemon_amount.isdigit() or int(pokemon_amount) <= 0:
                    print("\nInvalid number! Please enter a positive integer.")
                    continue  # Keep asking if invalid number
                break  # Exit loop if valid number is entered

            while True:  # Loop until valid input for highest/lowest is received
                order = input("Find pokemon in the order from the highest or lowest? (h/l): ").strip().lower()
                if order == "h":
                    highest = True
                    break
                elif order == "l":
                    highest = False
                    break
                else:
                    print("\nInvalid input! Please enter 'h' for highest or 'l' for lowest.")

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