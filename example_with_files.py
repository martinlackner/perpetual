# Example that loads profiles from files.

# Author: Benjamin Krenn

from __future__ import print_function
import file_loader
import perpetual_rules as perpetual


def tsoi_example(dir_name, from_date=None, to_date=None):
    print("soi data from folder", dir_name)
    approval_profiles, voters = \
        file_loader.start_tsoi_load(dir_name, 10, from_date=from_date,
                                    to_date=to_date)
    weights = perpetual.init_weights("per_quota", voters)
    for approval_profile in approval_profiles:
        print("Perpetual Quota selects", perpetual.per_quota(
            approval_profile, weights))


def csv_example(dir_name, from_date=None, to_date=None):
    print("Spotify csv data")
    approval_profiles, voters = \
        file_loader.start_spotify_csv_load(dir_name, 0.7,
                                           from_date=from_date,
                                           to_date=to_date)
    weights = perpetual.init_weights("per_quota", voters)
    for approval_profile in approval_profiles:
        print("Perpetual Quota selects", perpetual.per_quota(
            approval_profile, weights))


tsoi_example("data/", from_date="20170309", to_date="20170316")
csv_example("spotify/", from_date="20161230", to_date="20161230")