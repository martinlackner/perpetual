# Example that loads profiles from files.

# Author: Benjamin Krenn

from __future__ import print_function
import sys
sys.path.insert(0, '..')
import file_loader
import perpetual_rules as perpetual


# tsoi and ttoi are opened the same way
def file_example(dir_name, from_date=None, to_date=None):
    method = "per_quota"
    print("Loading tsoi profiles from {}".format(
        dir_name))
    approval_profiles, voters = \
        file_loader.start_file_load(dir_name, 2, from_date=from_date,
                                    to_date=to_date, with_weights=False)
    for i in range(len(approval_profiles)):
        print("{}: {}".format(i, approval_profiles[i]))
    weights = perpetual.init_weights(method, voters)
    winners = perpetual.compute_rule_sequence(method,
                                              approval_profiles,
                                              weights,
                                              missing_rule="all")
    print("Choice sequence for {}:\n {}".format(method, winners))

    print("\n-------------")
    print("Loading tsoi profiles from {}\n using candidate weights".format(
        dir_name))
    approval_profiles, voters = \
        file_loader.start_file_load(dir_name, 0.9, from_date=from_date,
                                    to_date=to_date, with_weights=True)
    for i in range(len(approval_profiles)):
        print("{}: {}".format(i, approval_profiles[i]))
    weights = perpetual.init_weights(method, voters)
    winners = perpetual.compute_rule_sequence(method,
                                              approval_profiles,
                                              weights,
                                              missing_rule="all")
    print("Choice sequence for {}:\n {}".format(method, winners))


file_example("examples/example_files/")
