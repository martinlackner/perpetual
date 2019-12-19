from __future__ import print_function
import pickle
from os.path import exists
import random

import experiments
from experiments import basic_stats, run_exp_for_history, \
    statistical_significance, plot_data
from perpetual_rules import PERPETUAL_RULES


rules = ["av",
         "per_pav",
         "per_equality",
         "per_quota",
         "per_nash",
         "per_reset",
         "per_unitcost",
         "per_consensus",
         "serial_dictatorship",
         ]

random.seed(31415)

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

    aver_quotacompl = {rule: [] for rule in PERPETUAL_RULES}
    max_quotadeviation = {rule: [] for rule in PERPETUAL_RULES}
    aver_satisfaction = {rule: [] for rule in PERPETUAL_RULES}
    aver_influencegini = {rule: [] for rule in PERPETUAL_RULES}

    print()
    print(spec, "with", len(curr_instances), "instances")
    basic_stats(curr_instances)

    picklefile = "../pickle/computation-" + name + ".pickle"
    if not exists(picklefile):
        print("computing perpetual voting rules")

        for history in curr_instances:
            run_exp_for_history(history,
                                aver_quotacompl,
                                max_quotadeviation,
                                aver_satisfaction,
                                aver_influencegini)

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

    # analyze_exp_results(exp_name, aver_quotacompl, max_quotadeviation)

    statistical_significance(aver_quotacompl, aver_influencegini)

    # create plots
    plot_data(exp_name,
              aver_quotacompl,
              max_quotadeviation,
              aver_satisfaction,
              aver_influencegini,
              rules)

print("Done")
