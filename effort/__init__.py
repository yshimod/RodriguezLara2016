from otree.api import *
import random

doc = """
努力課題
"""


class C(BaseConstants):
    NAME_IN_URL = 'effort'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    effort_score = models.IntegerField()


# PAGES
class Task(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.effort_score = player.effort_score = random.choice(list(range(21)))


class Results(Page):
    pass


page_sequence = [Task, Results]
