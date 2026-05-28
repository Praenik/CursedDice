from random import randint


def roll_dice(dice, modifier=0):
    return max(1, randint(1, dice) + modifier)


def roll_d20(modifier=0):
    return randint(1, 20) + modifier
