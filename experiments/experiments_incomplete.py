from __future__ import print_function

import random
from os.path import exists
import pickle

from experiments import run_exp_for_history, statistical_significance, \
    plot_data, basic_stats
import sys
sys.path.insert(0, '..')
import file_loader
from perpetual_rules import PERPETUAL_RULES


# experiments from files
random.seed(31415)

rules = ["av",
         "per_pav",
         "per_equality",
         "per_quota",
         "per_nash",
         "per_reset",
         "per_unitcost",
         "per_consensus",
         "serial_dictatorship",
         "per_quota_mod",
         "rotating_dictatorship",
         "rotating_serial_dictatorship",
         "min_dry_spell"
         ]

# This example uses data from
# https://www.dbai.tuwien.ac.at/proj/sudema/temporaldata.html
# to test this it needs to be downloaded.
# The section "All the above tsoi as one download"
# can be downloaded and extracted in the root of this project
# input_dirs holds the directory paths to the data
# they are relative to the root of this project
input_dirs = ["data/eurovision_song_contest_tsoi",
              "data/i_phone/games/free_games_tsoi",
              "data/i_phone/news/free_news_tsoi",
              "data/i_phone/games/gross_games_tsoi",
              "data/i_phone/news/gross_news_tsoi",
              "data/i_phone/games/paid_games_tsoi",
              "data/i_phone/news/paid_news_tsoi",
              "data/spotify/weekly_tsoi",
              "data/spotify/viral_weekly_tsoi",
              "data/spotify/daily_tsoi",
              "data/spotify/viral_daily_tsoi",
              ]

weighted_input_dirs = ["data/spotify/daily_tsoi",
                       "data/spotify/weekly_tsoi"]

# Rules for replacing missing voter data, None leads to exception
missing_rules = [None, "all", "empty", "ignore"]

for missing_rule in missing_rules[1:]:
    print("Now start experiments with files from", input_dirs, end=' ')
    print("With replacement rule ", missing_rule)

    aver_quotacompl = {rule: [] for rule in PERPETUAL_RULES}
    max_quotadeviation = {rule: [] for rule in PERPETUAL_RULES}
    aver_satisfaction = {rule: [] for rule in PERPETUAL_RULES}
    aver_influencegini = {rule: [] for rule in PERPETUAL_RULES}

    data_instances = []
    instance_size = 20
    multiplier = 1
    percent = 0.9
    for _ in range(0, 6):
        for directory in input_dirs:
            if directory is "data/eurovision_song_contest_tsoi" \
                    and multiplier > 3:
                continue
            history, _ = \
                file_loader.start_file_load(
                        directory,
                        threshold=2*multiplier)

            splits = int(len(history) / instance_size)
            for i in range(0, splits):
                data_instances.append(
                    history[i*instance_size:(i+1)*instance_size])

        for directory in weighted_input_dirs:
            history, _ = \
                file_loader.start_file_load(
                    directory,
                    threshold=percent,
                    with_weights=True)
            splits = int(len(history) / instance_size)
            for i in range(0, splits):
                data_instances.append(
                    history[i*instance_size:(i+1)*instance_size])

        multiplier += 1
        percent -= 0.14

    print("number of instances:", len(data_instances))
    basic_stats(data_instances)

    picklefile = "../pickle/computation-" + "tsoi_data_" + missing_rule\
                 + ".pickle"
    if not exists(picklefile):
        print("computing perpetual voting rules")
        for history in data_instances:
            run_exp_for_history(history,
                                aver_quotacompl,
                                max_quotadeviation,
                                aver_satisfaction,
                                aver_influencegini,
                                missing_rule=missing_rule)

        print("writing results to", picklefile)
        with open(picklefile, 'wb') as f:
            pickle.dump([aver_quotacompl, max_quotadeviation,
                         aver_satisfaction, aver_influencegini], f,
                        protocol=2)
    else:
        print("loading results from", picklefile)
        with open(picklefile, 'rb') as f:
            (aver_quotacompl, max_quotadeviation,
             aver_satisfaction, aver_influencegini) = pickle.load(f)

    statistical_significance(aver_quotacompl, aver_influencegini)

    # create plots
    plot_data("tsoi_data_" + missing_rule,
              aver_quotacompl,
              max_quotadeviation,
              aver_satisfaction,
              aver_influencegini,
              rules)

    print("Done with files and missing rule")
