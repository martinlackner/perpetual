# A simple example

# Author: Martin Lackner

from __future__ import print_function
import sys
sys.path.insert(0, '..')
import profiles
import perpetual_rules as perpetual


apprsets1 = {1: [1], 2: [1], 3: [2], 4: [3]}
apprsets2 = {1: [1], 2: [2], 3: [2], 4: [3]}
apprsets3 = {1: [1], 2: [1], 3: [2], 4: [3]}
voters = [1, 2, 3, 4]
cands = [1, 2, 3]
profile1 = profiles.ApprovalProfile(voters, cands, apprsets1)
profile2 = profiles.ApprovalProfile(voters, cands, apprsets2)
profile3 = profiles.ApprovalProfile(voters, cands, apprsets3)

weights = perpetual.init_weights("per_quota", voters)

print("First round:")
print("Perpetual Quota selects", perpetual.per_quota(profile1, weights))

print("Second round:")
print("Perpetual Quota selects", perpetual.per_quota(profile2, weights))

print("Third round:")
print("Perpetual Quota selects", perpetual.per_quota(profile3, weights))
