import requests

def get_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extracting details
        name = data["name"].capitalize()
        abilities = [ability["ability"]["name"] for ability in data["abilities"]]
        types = [poke_type["type"]["name"] for poke_type in data["types"]]
        weight = data["weight"]
        height = data["height"]

        # Displaying information
        print(f"Name: {name}")
        print(f"Abilities: {', '.join(abilities)}")
        print(f"Types: {', '.join(types)}")
        print(f"Weight: {weight}")
        print(f"Height: {height}")
    
    else:
        print("Pokémon not found. Please check the name and try again.")

# Example usage
pokemon_name = input("Enter Pokémon name: ")
get_pokemon_data(pokemon_name)
