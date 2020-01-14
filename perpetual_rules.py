# Implementations of perpetual voting rules

# Author: Martin Lackner
"""Implementation of perpetual voting rules
"""


from future.utils import iteritems

try:
    from gmpy2 import mpq as Fraction
except ImportError:
    from fractions import Fraction

import random
import copy

PERPETUAL_RULES = ["per_pav",
                   "per_consensus",
                   "per_majority",
                   "per_unitcost",
                   "per_reset",
                   "per_nash",
                   "per_equality",
                   "av",
                   "per_phragmen",
                   # "per_multiplication_offset",
                   "per_quota",
                   "per_quota_mod",
                   # "per_quota_min",
                   "serial_dictatorship",
                   "random_dictatorship",
                   "per_2nd_prize",
                   "rotating_dictatorship",
                   "rotating_serial_dictatorship"
                   ]
"""List of available voting rules."""

SHORT_RULENAMES = {"per_pav": "Per. PAV",
                   "per_consensus": "Per. Cons.",
                   "per_majority": "p-Subn/2",
                   "per_unitcost": "Per. Unit-Cost",
                   "per_reset": "Per. Reset",
                   "per_nash": "Per. Nash",
                   "per_equality": "Per. Equality",
                   "av": "AV",
                   "per_phragmen": "Per. Phrag.",
                   "per_multiplication_offset": "p-Mult-off",
                   "per_quota": "Per. Quota",
                   "per_quota_mod": "Per. Quota mod",
                   "per_quota_min": "p-Quo-min",
                   "serial_dictatorship": "Rand. Serial Dict.",
                   "random_dictatorship": "SD",
                   "per_2nd_prize": "p-2nd",
                   "rotating_dictatorship": "Rot. Dict.",
                   "rotating_serial_dictatorship": "Rot. Serial Dict."
                   }
"""Dictionary with shortcuts for the rule names."""


def compute_rule_sequence(rule, profile_list, weights=None,
                          missing_rule=None):
    """Starting point for computing a perpetual voting rule multiple times.

    Parameters
    ----------
    rule : str
        The name of the rule that is used.

    profile_list : ApprovalProfile list
        The approval profile to use the rule on.

    weights : tuple or dict, optional
        The weights of each voter.

    missing_rule : str, optional
        The rule that is used if a voter is missing from the profile.

    Returns
    -------
    list
        A list of winners (each input profile one winner)
    """
    winner_history = []
    for profile in profile_list:
        winner_history.append(compute_rule(rule, profile, weights,
                                           missing_rule))
    return winner_history


def compute_rule(rule, profile, weights=None, missing_rule=None):
    """Starting point for computing a perpetual voting rule one time.

    Parameters
    ----------
    rule : str
        The name of the rule that is used.

    profile : ApprovalProfile
        The approval profile to use the rule on.

    weights : tuple or dict, optional
        The weights of each voter.

    missing_rule : str, optional
        The rule that is used if a voter is missing from the profile.

    Returns
    -------
    winner
        The winner according to the rule
    """
    if rule == "per_quota" or rule == "per_quota_min" \
            or rule == "per_quota_mod":
        voters = weights[0].keys()
    else:
        voters = weights.keys()
    if missing_rule == "empty":
        profile = copy.deepcopy(profile)
        for voter in voters:
            if voter not in profile.voters:
                profile.voters.append(voter)
                profile.approval_sets[voter] = []
    elif missing_rule == "all":
        profile = copy.deepcopy(profile)
        for voter in voters:
            if voter not in profile.voters:
                profile.voters.append(voter)
                profile.approval_sets[voter] = list(profile.cands)

    elif missing_rule == "ignore":
        pass
    else:
        for voter in voters:
            if voter not in profile.voters:
                raise Exception("Missing voter")

    if rule == "per_pav":
        return per_pav(profile, weights)
    elif rule == "per_consensus":
        return per_consensus(profile, weights)
    elif rule == "per_unitcost":
        return per_unitcost(profile, weights)
    elif rule == "per_reset":
        return per_reset(profile, weights)
    elif rule == "per_nash":
        return per_nash(profile, weights)
    elif rule == "per_equality":
        return per_equality(profile, weights)
    elif rule == "av":
        return av(profile)
    elif rule == "per_phragmen":
        return per_phragmen(profile, weights)
    elif rule == "per_quota":
        return per_quota(profile, weights)
    elif rule == "per_quota_mod":
        return per_quota_mod(profile, weights)
    elif rule == "per_quota_min":
        return per_quota_min(profile, weights)
    elif rule == "random_dictatorship":
        return random_dictatorship(profile)
    elif rule == "serial_dictatorship":
        return serial_dictatorship(profile)
    elif rule == "per_majority":
        return per_majority(profile, weights)
    elif rule == "per_2nd_prize":
        return per_2nd_prize(profile, weights)
    elif rule == "rotating_dictatorship":
        return rotating_dictatorship(profile, weights)
    elif rule == "rotating_serial_dictatorship":
        return rotating_serial_dictatorship(profile, weights)
    else:
        raise NotImplementedError("rule " + str(rule) + " unknown")


def init_weights(rule, voters):
    """Generates a weight object for the given rule with and all
    the voters

    Parameters
    ----------
    rule : str
        The name of the rule that is used.

    voters : list
        A list with all voters.

    Returns
    -------
    weights
        The initial weights for the rule.
    """
    if (rule == "per_multiplication_offset" or
            rule == "per_nash" or
            rule == "per_equality" or
            rule == "per_phragmen"):
        return dict.fromkeys(voters, 0)
    elif (rule == "per_quota"
            or rule == "per_quota_min"
            or rule == "per_quota_mod"):
        return (dict.fromkeys(voters, 0), dict.fromkeys(voters, 0))
    else:
        return dict.fromkeys(voters, 1)


########################################################################
# PERPETUAL VOTING RULES (APPROVAL-BASED) ##############################
########################################################################

def per_pav(profile, weights):
    score = {}
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] += weights[v]
    maxsc = max(score.values())
    # return false if winner is not unique
    # if len([c for c in profiles.cands if score[c] == maxsc])>1:
    #     return False
    winner = [c for c in profile.cands if score[c] == maxsc][0]
    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            weights[v] = Fraction(1, (Fraction(1) / weights[v] + 1))  # 1/x --> 1/(x+1)
    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def per_consensus(profile, weights):
    return __per_subtraction(profile, weights, subtr_mode="per_consensus")


def per_unitcost(profile, weights):
    return __per_subtraction(profile, weights, subtr_mode="per_unitcost")


def per_reset(profile, weights):
    return __per_subtraction(profile, weights, subtr_mode="zero")


def per_majority(profile, weights):
    return __per_subtraction(profile, weights, subtr_mode="numvoters_half")


def per_2nd_prize(profile, weights):
    return __per_subtraction(profile, weights, subtr_mode="per_2nd_prize")


def __per_subtraction(profile, weights, subtr_mode="numvoters"):
    score = {}
    candidate_support = dict.fromkeys(profile.cands, 0)
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v] and weights[v] > 0:
                score[c] += weights[v]
                candidate_support[c] += 1
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc][0]
    for v in profile.voters:
        if subtr_mode == "per_consensus":
            if winner in profile.approval_sets[v] and weights[v] > 0:
                weights[v] -= Fraction(len(profile.voters),
                                  candidate_support[winner])
        elif subtr_mode == "per_2nd_prize":
            if len(score) > 1:
                second_prize = sorted(score.values())[-2]
            else:
                second_prize = list(score.values())[0]
            factor = 1 - 1. * second_prize / score[winner]
            if winner in profile.approval_sets[v] and weights[v] > 0:
                weights[v] *= factor
        elif subtr_mode == "numvoters_half":
            if winner in profile.approval_sets[v] and weights[v] > 0:
                weights[v] -= Fraction(len(profile.voters),
                                  2 * candidate_support[winner])
        elif subtr_mode == "per_unitcost":
            if winner in profile.approval_sets[v]:
                weights[v] -= 1
        elif subtr_mode == "zero":
            if winner in profile.approval_sets[v]:
                weights[v] = 0
        else:
            raise NotImplementedError("'" + str(subtr_mode)
                                      + "' is not a known subtraction mode")
    for v in profile.voters:
        weights[v] += 1

    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def per_nash(profile, weights):
    score = {}
    for c in profile.cands:
        score[c] = 1
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] *= weights[v] + 1
            else:
                if weights[v] == 0:
                    # multiply by a small epsilon
                    score[c] *= Fraction(1, max(sum(weights.values()),
                                           len(profile.voters)))
                else:
                    score[c] *= weights[v]
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc][0]
    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            weights[v] += 1
    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def per_equality(profile, weights):
    score = {}
    minweight = min(weights.values())
    maxweight = max(weights.values())
    possible_winners = list(profile.cands)
    for bound in range(minweight, maxweight + 1):
        for c in profile.cands:
            score[c] = 0
            for v in profile.voters:
                if c in profile.approval_sets[v] and weights[v] <= bound:
                    score[c] += 1
        maxsc = max([score[c] for c in possible_winners])
        possible_winners = [c for c in possible_winners if score[c] == maxsc]
        if len(possible_winners) == 1:
            break
    winner = possible_winners[0]
    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            weights[v] += 1
    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def av(profile):
    score = {}
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] += 1
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc][0]
    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def per_phragmen(profile, weights):
    averageload = {}
    for c in profile.cands:
        supporters = [v for v in profile.voters
                      if c in profile.approval_sets[v]]
        if len(supporters) == 0:
            averageload[c] = float('inf')
        else:
            while True:
                averageload[c] = Fraction(
                    1 + sum([weights[v] for v in supporters]),
                    len(supporters))
                if averageload[c] >= max([weights[v] for v in supporters]):
                    break
                else:
                    supporters = [v for v in profile.voters
                                  if c in profile.approval_sets[v]
                                  and weights[v] <= averageload[c]]
    minload = min(averageload.values())
    winner = [c for c in profile.cands if averageload[c] == minload][0]
    for v in profile.voters:
        if winner in profile.approval_sets[v] and weights[v] < minload:
            weights[v] = minload
    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


# keep the perpetual-lower quota as small as possible
def per_quota_min(profile, weights, supportbasedtiebreaking=False):
    per_quota, satisfaction = weights

    cand_support = {c: 0 for c in profile.cands}
    for voter in profile.voters:
        for c in profile.approval_sets[voter]:
            cand_support[c] += 1

    for v in profile.voters:
        support = max([cand_support[c]
                       for c in profile.approval_sets[v]] + [0])
        per_quota[v] += Fraction(support, len(profile.voters))

    score = {}
    candidate_support = dict.fromkeys(profile.cands, 0)
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] += min(1, max(0, per_quota[v] - satisfaction[v]))
                candidate_support[c] += 1
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc]
    if supportbasedtiebreaking:
        winner = sorted(winner, reverse=True,
                        key=lambda c: candidate_support[c])[0]
    else:
        winner = winner[0]

    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            satisfaction[v] += 1

    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


# original implementation: with special tie-breaking and
# violations > 1 count more
def per_quota(profile, weights, supportbasedtiebreaking=False):
    per_quota, satisfaction = weights

    cand_support = {c: 0 for c in profile.cands}
    for voter in profile.voters:
        for c in profile.approval_sets[voter]:
            cand_support[c] += 1

    for v in profile.voters:
        support = max([cand_support[c]
                       for c in profile.approval_sets[v]] + [0])
        per_quota[v] += Fraction(support, len(profile.voters))

    score = {}
    candidate_support = dict.fromkeys(profile.cands, 0)
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] += max(0, per_quota[v] - satisfaction[v])
                candidate_support[c] += 1
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc]
    if supportbasedtiebreaking:
        winner = sorted(winner, reverse=True,
                        key=lambda c: candidate_support[c])[0]
    else:
        winner = winner[0]

    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            satisfaction[v] += 1

    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


# modification of Perpetual Quota
# based on qu_k - sat_k
def per_quota_mod(profile, weights, supportbasedtiebreaking=True):
    per_quota, satisfaction = weights
    support = {}
    cand_support = {c: 0 for c in profile.cands}
    for voter in profile.voters:
        for c in profile.approval_sets[voter]:
            cand_support[c] += 1

    for v in profile.voters:
        support[v] = max([cand_support[c]
                         for c in profile.approval_sets[v]] + [0])

    score = {}
    candidate_support = dict.fromkeys(profile.cands, 0)
    for c in profile.cands:
        score[c] = 0
        for v in profile.voters:
            if c in profile.approval_sets[v]:
                score[c] += max(0, per_quota[v] - satisfaction[v])
                candidate_support[c] += 1
    maxsc = max(score.values())
    winner = [c for c in profile.cands if score[c] == maxsc]
    if supportbasedtiebreaking:
        winner = sorted(winner, reverse=True,
                        key=lambda c: candidate_support[c])[0]
    else:
        winner = winner[0]

    for v in profile.voters:
        if winner in profile.approval_sets[v]:
            satisfaction[v] += 1

        per_quota[v] += Fraction(support[v], len(profile.voters))

    # tied_winners = [c for c in profiles.cands if score[c] == maxsc]
    return winner


def random_dictatorship(profile):
    voters = [v for (v, appr) in iteritems(profile.approval_sets)
              if len(appr) > 0]
    dictator = random.choice(voters)
    return random.choice(profile.approval_sets[dictator])


def serial_dictatorship(profile):
    cands = set(profile.cands)
    voters = list(profile.voters)
    random.shuffle(voters)
    for v in voters:
        if cands & set(profile.approval_sets[v]):
            cands = cands & set(profile.approval_sets[v])
    return random.choice(list(cands))


def rotating_dictatorship(profile, weights):
    voters = [v for (v, appr) in iteritems(profile.approval_sets)
              if len(appr) > 0]
    possible_dictators = []
    for voter, weight in iteritems(weights):
        if weight == 0 and voter in voters:
            possible_dictators.append(voter)
    if len(possible_dictators) > 0:
        dictator = sorted(possible_dictators)[0]
        winner = profile.approval_sets[dictator][0]
        weights[dictator] = 1
        return winner
    else:
        voters = sorted(voters)
        dictator = voters[0]
        for voter in weights:
            weights[voter] = 0
        weights[dictator] = 1
        return profile.approval_sets[dictator][0]


def rotating_serial_dictatorship(profile, weights):
    voters = [v for (v, appr) in iteritems(profile.approval_sets)
              if len(appr) > 0]
    voters = sorted(voters)
    possible_dictators = []
    cands = set(profile.cands)
    for voter, weight in iteritems(weights):
        if weight == 0 and voter in voters:
            possible_dictators.append(voter)
    if len(possible_dictators) > 0:
        dictator = sorted(possible_dictators)[0]
        weights[dictator] = 1
        for v in voters[voters.index(dictator):]:
            if cands & set(profile.approval_sets[v]):
                cands = cands & set(profile.approval_sets[v])
        return sorted(list(cands))[0]
    else:
        dictator = voters[0]
        for voter in weights:
            weights[voter] = 0
        weights[dictator] = 1
        for v in voters:
            if cands & set(profile.approval_sets[v]):
                cands = cands & set(profile.approval_sets[v])
        return sorted(list(cands))[0]
