import socket
import json
import random
import re

HOST = 'localhost'
PORT = 12345

def roll_dice(sides):
    return random.randint(1, sides)

def parse_dice_expression(expr):
    """Parses and evaluates a dice expression like '1d4,2d6,3'."""
    tokens = expr.split(',')
    total = 0
    details = []

    for token in tokens:
        token = token.strip()
        dice_match = re.match(r"(\d*)d(\d+)", token)
        if dice_match:
            num = int(dice_match.group(1)) if dice_match.group(1) else 1
            sides = int(dice_match.group(2))
            rolls = [random.randint(1, sides) for _ in range(num)]
            total += sum(rolls)
            details.append(f"{num}d{sides}: {rolls}")
        elif token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
            mod = int(token)
            total += mod
            details.append(f"mod: {mod}")
        else:
            raise ValueError(f"Invalid token: '{token}'")

    return total, details

def main():
    username = input("Enter your character name: ")
    character = {
        "name": username,
        "class": "Fighter",
        "level": 1,
        "hp": 10,
    }

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Register with the server
    register_msg = {
        "type": "register",
        "username": username,
        "character": character
    }
    client.send(json.dumps(register_msg).encode())

    while True:
        command = input("Type 'roll 1d20/2d4/ect', 'get all', or 'quit': ").strip()
        if command == "quit":
            break
        elif command.startswith("roll"):
            try:
                _, expr = command.split(" ", 1)
                result, breakdown = parse_dice_expression(expr)
                roll_msg = {
                    "type": "roll",
                    "username": username,
                    "dice": expr,
                    "result": result
                }
                client.send(json.dumps(roll_msg).encode())
                print(f"You rolled {result} ({'; '.join(breakdown)})")
            except Exception as e:
                print(f"Error: {e}")
        elif command == "get all":
            client.send(json.dumps({"type": "get_all_characters", "username": username}).encode())
            response = client.recv(4096).decode()
            print("All Characters:")
            print(json.dumps(json.loads(response)["data"], indent=2))
        else:
            print("Unknown command.")

    client.close()

if __name__ == "__main__":
    main()
