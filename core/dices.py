from random import randint


def roll_dice(dice: int, *modifier) -> int:
    roll = randint(1, dice)
    total = roll + sum(modifier)
    return max(1, total)


def roll_d20(*modifier) -> int:
    return randint(1, 20) + sum(modifier)
