# Preferences profiles for perpetual voting rules

# Author: Martin Lackner

import copy
import numpy.random as random
from scipy.spatial.distance import euclidean
from future.utils import iteritems


# approval profile
class ApprovalProfile(object):
    def __init__(self, voters, cands, approval_sets):
        self.voters = voters
        self.approval_sets = approval_sets
        self.cands = cands
        for v, appr in iteritems(self.approval_sets):
            for c in appr:
                if v not in voters:
                    raise Exception(str(v) + " is not a valid voter; "
                                    + "voters are " + str(voters)+".")
                if c not in cands:
                    raise Exception(str(c) + " is not a valid candidate; "
                                    + "candidates are " + str(cands) + ".")

    def __str__(self):
        return ("Profile with %d votes and %d candidates: "
                % (len(self.voters), len(self.cands))
                + ', '.join(map(str, self.approval_sets.values())))

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        voters = list(self.voters)
        approvals_sets = copy.deepcopy(self.approval_sets)
        cands = list(self.cands)
        return ApprovalProfile(voters, cands, approvals_sets)


# uniformly random profile:
# voters' approval sets have a size given by dict approval_set_sizes
def uniformly_random_profile(voters, cands, approval_set_sizes):
    approval_sets = {}
    for v in voters:
        approval_sets[v] = set(random.choice(cands, approval_set_sizes[v],
                                             replace=False))
    return ApprovalProfile(voters, cands, approval_sets)


# create approval profile from 2d coordinates (Euclidean distance)
def approvalprofile_from_2d_euclidean(voters, cands, voter_points,
                                      cand_points, threshold):
    approval_sets = {}
    for v in voters:
        distances = {c: euclidean(voter_points[v], cand_points[c])
                     for c in cands}
        mindist = min(distances.values())
        approval_sets[v] = [c for c in cands
                            if distances[c] <= mindist * threshold]
    return ApprovalProfile(voters, cands, approval_sets)
