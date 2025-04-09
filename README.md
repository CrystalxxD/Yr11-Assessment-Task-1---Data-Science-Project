# Pokemon Finder
This Python program allows you to retrieve information on pokemon from an external API. The program uses the `requests`, `aiohttp`, `difflib`, `random `, `json`, `os`, `asynico` which allows the program to run smoothly and faster when calling api as well as storing data, randomly generating moves that the pokemon uses and finding the closest pokemon to the name that the user has typed.

## Features
- Fetches pokemon info on height, weight, id, moves, held items, special attacks and defence, hp etc.
- Orders pokemon by their stats
- Store past searched pokemon
- Deleting past searched pokemon

## URL for poke api
https://pokeapi.co/api/v2/

## Requirements
To run this program, you need to install the following dependencies: 
- `requests` For sending HTTP requests 
- `aiohttp` # For asynchronous HTTP requests. (makes getting the pokemon faster)

### Install dependencies
To install the required dependencies, you can run:

```bash
pip install -r requirements.txt