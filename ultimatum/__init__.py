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
    # group 分けをランダム化．
    subsession.group_randomly()

    # シナリオの順番を sessions.vars に格納．
    tmporder = ["ult", "nvc"]    # デフォルトの順番．
    if not subsession.session.config["ult_is_first"]:
        # session.config の ult_is_first が True ならば，デフォルトの順番を逆転させる．
        tmporder.reverse()
    subsession.session.vars["scenario_order"] = tmporder    # sessions.vars はリストを JSON 文字列化せず，直接代入して良い．

    # group ごと，努力課題の単価（a_p，a_r）と，報酬支払対象のシナリオを，ランダムに決定して記録しておく．
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

    # 報酬支払対象のシナリオ
    realized = models.StringField()    # 文字列 "ult" または "nvc" が入る．


class Player(BasePlayer):
    # 各シナリオの利得
    payoff_ult = models.FloatField()
    payoff_nvc = models.FloatField()


# 提案額の最大値の定義
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
    """
    努力課題の後，最初に到達する待機ページ．
    """
    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        group のメンバーが集まったタイミングで，パイの大きさ（提案額の最大値）を計算する．
        """
        # 各役割の player のオブジェクトを取得する．
        proposer: Player = group.get_player_by_role(C.PROPOSER_ROLE)
        responder: Player = group.get_player_by_role(C.RESPONDER_ROLE)

        # participant.effort_score に入っている努力課題のスコアを group のフィールドに転記する．
        group.q_p = proposer.participant.effort_score
        group.q_r = responder.participant.effort_score

        # パイの大きさを計算する．
        group.pie_p = group.q_p * group.a_p
        group.pie_r = group.q_r * group.a_r
        group.pie_tot = group.pie_p + group.pie_r


class Info(Page):
    """
    努力課題のスコアと稼いだ金額を呈示する．
    """
    pass


class Instruction(Page):
    """
    インストラクション．
    """
    pass


class InstructionWaitPage(WaitPage):
    """
    1つ目のシナリオの意思決定を開始するタイミングを group で揃えるための待機ページ．
    """
    pass


class Proposer1(Page):
    """
    1つ目のシナリオの proposer の意思決定ページ．
    """
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
        """
        scenario_order の0番目に対応したフィールド名に切り替える．
        """
        flag = player.session.vars["scenario_order"][0]    # 文字列 "ult" または "nvc" のいずれか．
        return [f"offer_p_{flag}"]    # flag が "ult" であれば ["offer_p_ult"] が返される．

    @staticmethod
    def vars_for_template(player: Player):
        """
        シナリオ順と役割にしたがってテンプレートの中身を書き換えるための変数を返す．
        """
        flag = player.session.vars["scenario_order"][0]    # 文字列 "ult" または "nvc" のいずれか．
        return dict(
            scenario = flag,    # 文字列 "ult" または "nvc" のいずれか．
            scenarionum = 1,    # シナリオの順番
            role = C.PROPOSER_ROLE    # 役割
        )


class Responder1(Page):
    """
    1つ目のシナリオの responder の意思決定ページ．
    """
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
        """
        scenario_order の0番目に対応したフィールド名に切り替える．
        """
        flag = player.session.vars["scenario_order"][0]
        return [f"offer_r_{flag}"]

    @staticmethod
    def vars_for_template(player: Player):
        """
        シナリオ順と役割にしたがってテンプレートの中身を書き換えるための変数を返す．
        """
        flag = player.session.vars["scenario_order"][0]
        return dict(
            scenario = flag,
            scenarionum = 1,
            role = C.RESPONDER_ROLE
        )


class ScenarioWaitPage(WaitPage):
    """
    2つ目のシナリオの意思決定を開始するタイミングを group で揃えるための待機ページ．
    """
    pass


class Proposer2(Page):
    """
    2つ目のシナリオの proposer の意思決定ページ．
    """
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
        """
        scenario_order の1番目に対応したフィールド名に切り替える．
        """
        flag = player.session.vars["scenario_order"][1]
        return [f"offer_p_{flag}"]

    @staticmethod
    def vars_for_template(player: Player):
        """
        シナリオ順と役割にしたがってテンプレートの中身を書き換えるための変数を返す．
        """
        flag = player.session.vars["scenario_order"][1]
        return dict(
            scenario = flag,
            scenarionum = 2,
            role = C.PROPOSER_ROLE
        )


class Responder2(Page):
    """
    2つ目のシナリオの responder の意思決定ページ．
    """
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
        """
        scenario_order の1番目に対応したフィールド名に切り替える．
        """
        flag = player.session.vars["scenario_order"][1]
        return [f"offer_r_{flag}"]

    @staticmethod
    def vars_for_template(player: Player):
        """
        シナリオ順と役割にしたがってテンプレートの中身を書き換えるための変数を返す．
        """
        flag = player.session.vars["scenario_order"][1]
        return dict(
            scenario = flag,
            scenarionum = 2,
            role = C.RESPONDER_ROLE
        )


class ResultsWaitPage(WaitPage):
    """
    2つ目のシナリオの意思決定が終わった後，報酬を計算する待機ページ．
    """
    @staticmethod
    def after_all_players_arrive(group: Group):
        """
        報酬を計算する
        """
        proposer: Player = group.get_player_by_role(C.PROPOSER_ROLE)
        responder: Player = group.get_player_by_role(C.RESPONDER_ROLE)

        # ultimatum game の利得
        if group.offer_p_ult >= group.offer_r_ult:
            group.accepted_ult = True
            proposer.payoff_ult = group.pie_tot - group.offer_p_ult
            responder.payoff_ult = group.offer_p_ult
        else:
            group.accepted_ult = False
            proposer.payoff_ult = 0
            responder.payoff_ult = 0

        # no-veto-cost game の利得
        if group.offer_p_nvc >= group.offer_r_nvc:
            group.accepted_nvc = True
            proposer.payoff_nvc = group.pie_tot - group.offer_p_nvc
            responder.payoff_nvc = group.offer_p_nvc
        else:
            group.accepted_nvc = False
            proposer.payoff_nvc = group.pie_tot - group.offer_r_nvc
            responder.payoff_nvc = group.offer_r_nvc

        # 報酬支払対象のシナリオの利得を player.payoff に転記する．
        if group.realized == "ult":
            proposer.payoff = proposer.payoff_ult
            responder.payoff = responder.payoff_ult
        else:
            proposer.payoff = proposer.payoff_nvc
            responder.payoff = responder.payoff_nvc


class Results(Page):
    """
    結果をフィードバックするページ．
    """
    @staticmethod
    def vars_for_template(player: Player):
        group: Group = player.group

        # 各シナリオで辞書オブジェクトを定義し，キーを統一しておく．
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

        # 辞書オブジェクトを入れたリストを定義する．順番はデフォルトのシナリオ順に対応させる．
        results = [results_ult, results_nvc]

        firstgame =  player.session.vars["scenario_order"][0]

        # 1つ目のシナリオが nvc の場合（session.config の ult_is_first が True の場合）， results の順番を逆転させる．
        if firstgame == "nvc":
            results.reverse()

        # 報酬支払対象のシナリオが何番目のシナリオだったかを計算する．
        chosen_scenario = 1 if group.realized == firstgame else 2

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
