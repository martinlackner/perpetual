# Example that loads profiles from files.

# Author: Benjamin Krenn

from __future__ import print_function
import sys
sys.path.insert(0, '..')
import file_loader
import perpetual_rules as perpetual


def file_example(dir_name, from_date=None, to_date=None):
    print("tsoi data from folder", dir_name)
    approval_profiles, voters = \
        file_loader.start_tsoi_load(dir_name, 2, from_date=from_date,
                                    to_date=to_date, with_weights=False)
    weights = perpetual.init_weights("per_quota", voters)
    for approval_profile in approval_profiles:
        print("Perpetual Quota selects", perpetual.per_quota(
            approval_profile, weights))

    print("Now with using the weights from the tsoi")
    approval_profiles, voters = \
        file_loader.start_tsoi_load(dir_name, 0.9, from_date=from_date,
                                    to_date=to_date, with_weights=True)
    weights = perpetual.init_weights("per_quota", voters)
    winners = perpetual.compute_rule_sequence("per_quota",
                                              approval_profiles,
                                              weights,
                                              missing_rule="all")
    print("The list of winners is (first one first vote up to", end=' ')
    print("the last one for the last voting):\n", winners)


file_example("examples/example_files/", from_date="20170309",
             to_date="20170310")
