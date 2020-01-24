from __future__ import print_function

import random
from os.path import exists
import pickle


# experiments from files
import experiments
from experiments import run_exp_for_history, statistical_significance, \
    plot_data, basic_stats
import sys
sys.path.insert(0, '..')
import file_loader


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

# This part of the example is nearly the same as the aaai one,
# but it includes additional rules
exp_specs = [
    [10000, 20, 5, 20, 0.2, "eucl2", "uniform_square", 1.5]]
instances = experiments.generate_instances(exp_specs)

# run experiments, analyze and plot
for spec in exp_specs:
    if spec == "full":
        curr_instances = [inst for coll in instances.values()
                          for inst in coll]
    else:
        curr_instances = instances[str(spec)]

    name = str(spec).replace("]", "").replace("[", "")
    exp_name = str(name).replace(" ", "").replace("'", "")

    aver_quotacompl = {rule: [] for rule in rules}
    max_quotadeviation = {rule: [] for rule in rules}
    aver_satisfaction = {rule: [] for rule in rules}
    aver_influencegini = {rule: [] for rule in rules}

    print()
    print(spec, "with", len(curr_instances), "instances")
    basic_stats(curr_instances)

    picklefile = "../pickle/computation-extra-" + name + ".pickle"
    if not exists(picklefile):
        print("computing perpetual voting rules")

        for history in curr_instances:
            run_exp_for_history(history,
                                aver_quotacompl,
                                max_quotadeviation,
                                aver_satisfaction,
                                aver_influencegini,
                                rules)

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

    statistical_significance("perpetual lower quota compliance",
                             aver_quotacompl)
    statistical_significance("Gini influence coefficient",
                             aver_influencegini)
    statistical_significance("maximum quota deviation",
                             max_quotadeviation)
    statistical_significance("utilitarian voter satisfaction",
                             aver_satisfaction)

    # create plots
    plot_data("extra-" + exp_name,
              aver_quotacompl,
              max_quotadeviation,
              aver_satisfaction,
              aver_influencegini,
              rules)

print("Done")


# Nearly the same example as incomplete, but it only uses voters that
# are present in all profiles of a data set

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

print("Now starting experiments with files from", input_dirs)

aver_quotacompl = {rule: [] for rule in rules}
max_quotadeviation = {rule: [] for rule in rules}
aver_satisfaction = {rule: [] for rule in rules}
aver_influencegini = {rule: [] for rule in rules}

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
                threshold=2*multiplier,
                only_complete=True)

        splits = int(len(history) / instance_size)
        for i in range(0, splits):
            data_instances.append(
                history[i*instance_size:(i+1)*instance_size])

    for directory in weighted_input_dirs:
        history, _ = \
            file_loader.start_file_load(
                directory,
                threshold=percent,
                with_weights=True,
                only_complete=True)
        splits = int(len(history) / instance_size)
        for i in range(0, splits):
            data_instances.append(
                history[i*instance_size:(i+1)*instance_size])

    multiplier *= 2
    percent -= 0.14

print("number of instances:", len(data_instances))
basic_stats(data_instances)

picklefile = "../pickle/computation-" + "only_complete_tsoi_data.pickle"
if not exists(picklefile):
    print("computing perpetual voting rules")
    for history in data_instances:
        run_exp_for_history(history,
                            aver_quotacompl,
                            max_quotadeviation,
                            aver_satisfaction,
                            aver_influencegini,
                            rules)

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

statistical_significance("perpetual lower quota compliance",
                         aver_quotacompl)
statistical_significance("Gini influence coefficient",
                         aver_influencegini)
statistical_significance("maximum quota deviation",
                         max_quotadeviation)
statistical_significance("utilitarian voter satisfaction",
                         aver_satisfaction)

# create plots
plot_data("only_complete_tsoi_data",
          aver_quotacompl,
          max_quotadeviation,
          aver_satisfaction,
          aver_influencegini,
          rules)

print("Done with files (only complete voters allowed)")
