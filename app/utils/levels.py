import math
from app.core.constants import DifficultyLevel

def calculate_level_info(total_xp: int):

    lvl = int(0.5 + math.sqrt(0.25+ total_xp / 25))

    xp_for_current_lvl = 25 * lvl * (lvl-1)

    xp_for_next_lvl = 25 * lvl * (lvl+1)

    xp_in_current_lvl = total_xp - xp_for_current_lvl

    xp_required_for_next = xp_for_next_lvl - xp_for_current_lvl

    return {
        'level': lvl,
        'xp_current': xp_in_current_lvl,
        'xp_next': xp_required_for_next,
        'progress': round((xp_in_current_lvl / xp_required_for_next) * 100, 1)
    }


rewards = {DifficultyLevel.EASY: 10, DifficultyLevel.MEDIUM: 20, DifficultyLevel.HARD: 30}



