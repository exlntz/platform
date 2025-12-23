import math

WIN = 1.0
DRAW = 0.5
LOSS = 0.0

def calculate_elo_change(
        player_rating: float,
        opponent_rating: float,
        match_result: float,
        k: int = 32
) -> float:
    diff = (opponent_rating - player_rating) / 400

    E = 1 / (1 + math.pow(10,diff))

    rating_change = k * (match_result - E)

    return rating_change

#print(calculate_elo_change(1000,1200,WIN))