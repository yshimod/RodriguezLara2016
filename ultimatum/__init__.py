from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        group.a_p = 150
        group.a_r = random.choice([100, 150, 200])


class Group(BaseGroup):
    # 1問あたりのポイント
    a_p = models.FloatField()
    a_r = models.FloatField()

    # 正答数
    q_p = models.FloatField()
    q_r = models.FloatField()

    # 稼ぎ
    pie_p = models.FloatField()
    pie_r = models.FloatField()
    pie_tot = models.FloatField()

    # 意思決定
    offer_p = models.FloatField()
    offer_r = models.FloatField()

    # 結果
    accepted = models.BooleanField()


class Player(BasePlayer):
    payoff_ultimatum = models.FloatField()



# PAGES
class StartWaitPage(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):
        proposer = group.get_player_by_id(1)
        responder = group.get_player_by_id(2)

        group.q_p = proposer.participant.effort_score
        group.q_r = responder.participant.effort_score

        group.pie_p = group.q_p * group.a_p
        group.pie_r = group.q_r * group.a_r
        group.pie_tot = group.pie_p + group.pie_r


class Info(Page):
    pass


class Instruction(Page):
    pass


class InstructionWaitPage(WaitPage):
    pass


class Proposer(Page):
    form_model = "group"
    form_fields = ["offer_p"]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 1


class Responder(Page):
    form_model = "group"
    form_fields = ["offer_r"]

    @staticmethod
    def is_displayed(player):
        return player.id_in_group == 2


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        # ここで利得を計算する．
        pass

class Results(Page):
    pass


page_sequence = [
    StartWaitPage,
    Info,
    Instruction,
    InstructionWaitPage,
    Proposer,
    Responder,
    ResultsWaitPage,
    Results
]
