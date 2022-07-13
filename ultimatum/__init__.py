from otree.api import *
import random

doc = """
main task
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # 各 id_in_group にラベルをつける．
    PROPOSER_ROLE = "player A"    # id_in_group: 1
    RESPONDER_ROLE = "player B"    # id_in_group: 2


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    subsession.group_randomly()

    tmporder = ["ult", "nvc"]
    if not subsession.session.config["ult_is_first"]:
        tmporder.reverse()
    subsession.session.vars["scenario_order"] = tmporder

    for group in subsession.get_groups():
        group.a_p = 150
        group.a_r = random.choice([100, 150, 200])
        group.realized = random.choice(tmporder)


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
    offer_p_ult = models.FloatField()
    offer_r_ult = models.FloatField()
    offer_p_nvc = models.FloatField()
    offer_r_nvc = models.FloatField()

    # 結果
    accepted_ult = models.BooleanField()
    accepted_nvc = models.BooleanField()

    # 支払対象のゲーム
    realized = models.StringField()


class Player(BasePlayer):
    payoff_ult = models.FloatField()
    payoff_nvc = models.FloatField()


def offer_p_ult_max(group: Group):
    return group.pie_tot

def offer_r_ult_max(group: Group):
    return group.pie_tot

def offer_p_nvc_max(group: Group):
    return group.pie_tot

def offer_r_nvc_max(group: Group):
    return group.pie_tot


# PAGES
class StartWaitPage(WaitPage):

    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        group のメンバーが集まったタイミングで，パイの大きさ（提案額の最大値）を計算する．
        """
        # 各役割の player のオブジェクトを取得する．
        proposer: Player = group.get_player_by_role(C.PROPOSER_ROLE)
        responder: Player = group.get_player_by_role(C.RESPONDER_ROLE)

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


class Proposer1(Page):
    template_name = __name__ + "/decision.html"
    form_model = "group"

    @staticmethod
    def is_displayed(player: Player):
        """
        proposer にのみページを表示．
        """
        return player.role == C.PROPOSER_ROLE

    @staticmethod
    def get_form_fields(player: Player):
        flag = player.session.vars["scenario_order"][0]
        return ["offer_p_{}".format(flag)]

    @staticmethod
    def vars_for_template(player: Player):
        flag = player.session.vars["scenario_order"][0]
        return dict(
            scenario = flag,
            scenarionum = 1,
            role = C.PROPOSER_ROLE    # 役割
        )


class Responder1(Page):
    template_name = __name__ + "/decision.html"
    form_model = "group"

    @staticmethod
    def is_displayed(player: Player):
        """
        responder にのみページを表示．
        """
        return player.role == C.RESPONDER_ROLE

    @staticmethod
    def get_form_fields(player: Player):
        flag = player.session.vars["scenario_order"][0]
        return ["offer_r_{}".format(flag)]

    @staticmethod
    def vars_for_template(player: Player):
        flag = player.session.vars["scenario_order"][0]
        return dict(
            scenario = flag,
            scenarionum = 1,
            role = C.RESPONDER_ROLE
        )


class ScenarioWaitPage(WaitPage):
    pass


class Proposer2(Page):
    template_name = __name__ + "/decision.html"
    form_model = "group"

    @staticmethod
    def is_displayed(player: Player):
        """
        proposer にのみページを表示．
        """
        return player.role == C.PROPOSER_ROLE

    @staticmethod
    def get_form_fields(player: Player):
        flag = player.session.vars["scenario_order"][1]
        return ["offer_p_{}".format(flag)]

    @staticmethod
    def vars_for_template(player: Player):
        flag = player.session.vars["scenario_order"][1]
        return dict(
            scenario = flag,
            scenarionum = 2,
            role = C.PROPOSER_ROLE
        )


class Responder2(Page):
    template_name = __name__ + "/decision.html"
    form_model = "group"

    @staticmethod
    def is_displayed(player: Player):
        """
        responder にのみページを表示．
        """
        return player.role == C.RESPONDER_ROLE

    @staticmethod
    def get_form_fields(player: Player):
        flag = player.session.vars["scenario_order"][1]
        return ["offer_r_{}".format(flag)]

    @staticmethod
    def vars_for_template(player: Player):
        flag = player.session.vars["scenario_order"][1]
        return dict(
            scenario = flag,
            scenarionum = 2,
            role = C.RESPONDER_ROLE
        )


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        利得を計算する
        """
        proposer: Player = group.get_player_by_role(C.PROPOSER_ROLE)
        responder: Player = group.get_player_by_role(C.RESPONDER_ROLE)

        ## ultimatum game
        if group.offer_p_ult >= group.offer_r_ult:
            group.accepted_ult = True
            proposer.payoff_ult = group.pie_tot - group.offer_p_ult
            responder.payoff_ult = group.offer_p_ult
        else:
            group.accepted_ult = False
            proposer.payoff_ult = 0
            responder.payoff_ult = 0

        ## no-veto-cost game
        if group.offer_p_nvc >= group.offer_r_nvc:
            group.accepted_nvc = True
            proposer.payoff_nvc = group.pie_tot - group.offer_p_nvc
            responder.payoff_nvc = group.offer_p_nvc
        else:
            group.accepted_nvc = False
            proposer.payoff_nvc = group.pie_tot - group.offer_r_nvc
            responder.payoff_nvc = group.offer_r_nvc

        ## realized
        if group.realized == "ult":
            proposer.payoff = proposer.payoff_ult
            responder.payoff = responder.payoff_ult
        else:
            proposer.payoff = proposer.payoff_nvc
            responder.payoff = responder.payoff_nvc


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group: Group = player.group

        results_ult = dict(
            offer_p = group.offer_p_ult,
            offer_r = group.offer_r_ult,
            accepted = group.accepted_ult,
            payoff_tmp = player.payoff_ult
        )
        results_nvc = dict(
            offer_p = group.offer_p_nvc,
            offer_r = group.offer_r_nvc,
            accepted = group.accepted_nvc,
            payoff_tmp = player.payoff_nvc
        )

        results = [results_ult, results_nvc]

        firstgame =  player.session.vars["scenario_order"][0]

        if firstgame == "nvc":
            results.reverse()

        if group.realized == firstgame:
            chosen_scenario = 1
        else:
            chosen_scenario = 2

        return dict(
            results = results,
            chosen_scenario = chosen_scenario
        )


page_sequence = [
    StartWaitPage,
    Info,
    Instruction,
    InstructionWaitPage,
    Proposer1,
    Responder1,
    ScenarioWaitPage,
    Proposer2,
    Responder2,
    ResultsWaitPage,
    Results
]
