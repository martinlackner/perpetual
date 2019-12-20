from __future__ import print_function

import random
from os.path import exists
import pickle

import sys
sys.path.insert(0, '..')
import file_loader
from experiments import run_exp_for_history, statistical_significance, \
    plot_data, basic_stats
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
         "per_quota_mod"
         ]

# This example uses data from
# https://www.dbai.tuwien.ac.at/proj/sudema/temporaldata.html
# to test this it needs to be downloaded.
# input_dirs holds the directory paths to the data
# they are relative to the root of this project
input_dirs = ["data/eurovision_song_contest_tsoi",
              "data/free_games_tsoi",
              "data/free_news_tsoi",
              "data/gross_games_tsoi",
              "data/gross_news_tsoi",
              "data/paid_games_tsoi",
              "data/paid_news_tsoi",
              "data/weekly_tsoi",
              "data/viral_weekly_tsoi"]

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
            if directory.endswith("tsoi"):
                if directory is "data/eurovision_song_contest_tsoi" \
                        and multiplier > 3:
                    continue
                history, _ = \
                    file_loader.start_tsoi_load(
                            directory,
                            max_approvals=2*multiplier)
            elif directory.endswith("csv"):
                history, _ = \
                    file_loader.start_spotify_csv_load(
                            directory,
                            approval_percent=percent)
            else:
                continue

            splits = int(len(history) / instance_size)
            for i in range(0, splits):
                data_instances.append(
                    history[i*instance_size:(i+1)*instance_size])
        multiplier *= 2
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
            aver_quotacompl, max_quotadeviation, \
            aver_satisfaction, aver_influencegini = pickle.load(f)

    statistical_significance(aver_quotacompl, aver_influencegini)

    # create plots
    plot_data("tsoi_data_" + missing_rule,
              aver_quotacompl,
              max_quotadeviation,
              aver_satisfaction,
              aver_influencegini,
              rules)

    print("Done with files and missing rule")

