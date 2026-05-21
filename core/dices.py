from random import randint


def roll_dice(dice: int, *modifier) -> int:
    return max(1, randint(1, dice) + sum(modifier))


def roll_d20(*modifier) -> int:
    return randint(1, 20) + sum(modifier)
