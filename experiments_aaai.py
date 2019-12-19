from __future__ import print_function
import pickle
from os.path import exists
import random

import experiments
import profiles
from experiments import basic_stats, run_exp_for_history, \
    statistical_significance, plot_data
from perpetual_rules import PERPETUAL_RULES


# generate a list of 2d coordinates subject to
# various distributions
def generate_2d_points(agents, mode, sigma):

    points = {}
    # normal distribution, 1/3 of agents centered on (-0.5,-0.5),
    #                      2/3 of agents on (0.5,0.5)
    #                      all within [-1,1]x[-1,1]
    if mode == "eucl1":
        def within_bounds(point):
            return (point[0] <= 1 and point[0] >= -1 and
                    point[1] <= 1 and point[1] >= -1)
        for i in range(int(len(agents) / 3)):
            while True:
                points[agents[i]] = (random.gauss(-0.5, sigma),
                                     random.gauss(-0.5, sigma))
                if within_bounds(points[agents[i]]):
                    break
        for i in range(len(agents) / 3, len(agents)):
            while True:
                points[agents[i]] = (random.gauss(0.5, sigma),
                                     random.gauss(0.5, sigma))
                if within_bounds(points[agents[i]]):
                    break
    # normal distribution, 1/3 of agents centered on (-0.5,-0.5),
    #                      2/3 of agents on (0.5,0.5)
    elif mode == "eucl2":
        for i in range(int(len(agents) / 3)):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(int(len(agents) / 3), len(agents)):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(0.5, sigma))
    # normal distribution, 1/5 of agents centered on (-0.5,-0.5),
    #                      4/5 of agents on (0.5,0.5)
    elif mode == "eucl4":
        for i in range(len(agents) / 5):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(len(agents) / 5, len(agents)):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(0.5, sigma))
    # normal distribution, 3/5 of agents centered on (-0.25,0),
    #                      2/5 of agents on (0.25,0)
    elif mode == "eucl6":
        for i in range(2 * len(agents) / 5):
            points[agents[i]] = (random.gauss(-0.25, sigma),
                                 random.gauss(0, sigma))
        for i in range(2 * len(agents) / 5, len(agents)):
            points[agents[i]] = (random.gauss(0.25, sigma),
                                 random.gauss(0, sigma))
    # normal distribution
    elif mode == "normal":
        for i in range(len(agents)):
            points[agents[i]] = (random.gauss(0., sigma),
                                 random.gauss(0., sigma))
    # normal distribution, each 1/4 of agents centered on (+-0.5,+-0.5)
    elif mode == "eucl5":
        for i in range(len(agents) / 4):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(len(agents) / 4, 2 * len(agents) / 4):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(0.5, sigma))
        for i in range(2 * len(agents) / 4, 3 * len(agents) / 4):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(0.5, sigma))
        for i in range(3 * len(agents) / 4, len(agents)):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(-0.5, sigma))
    # normal distribution, 1/5 of agents centered on (-0.5,-0.5),
    #                      1/5 of agents centered on (-0.5,0.5),
    #                      1/5 of agents centered on (0.5,-0.5),
    #                      2/5 of agents on (0.5,0.5)
    elif mode == "eucl3":
        for i in range(len(agents) / 5):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(len(agents) / 5, 2 * len(agents) / 5):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(0.5, sigma))
        for i in range(2 * len(agents) / 5, 3 * len(agents) / 5):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(3 * len(agents) / 5, len(agents)):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(0.5, sigma))
    elif mode == "eucl2plus":
        for i in range(len(agents) / 6):
            points[agents[i]] = (random.gauss(-0.5, sigma),
                                 random.gauss(-0.5, sigma))
        for i in range(len(agents) / 6, len(agents)):
            points[agents[i]] = (random.gauss(0.5, sigma),
                                 random.gauss(0.5, sigma))
    elif mode == "uniform_square":
        for a in agents:
            points[a] = (random.uniform(-1, 1),
                         random.uniform(-1, 1))
    else:
        print("mode", mode, "not known")
        quit()
    return points


# generate instances for experiments according to specifications
def generate_instances(exp_specs):
    instances = {}
    for spec in exp_specs:
        if spec == "full":
            continue

        # load instances from a pickle file if it exists
        # or generate instances and save to pickle file
        name = str(spec).replace("]", "").replace("[", "")
        name = name.replace(" ", "").replace("'", "")
        picklefile = "pickle/experiments-" + name + ".pickle"
        if not exists(picklefile):
            print("generating instances for spec", spec)
            num_simulations, num_voters, num_cands, num_rounds, \
            sigma, voterpointmode, candpointmode, \
            approval_threshold = spec

            instances[str(spec)] = []
            for _ in range(num_simulations):

                voters = list(range(num_voters))
                cands = list(range(num_cands))
                voter_points = generate_2d_points(voters, voterpointmode,
                                                  sigma)

                # plt.scatter([x for x,y in voter_points.values()],
                #             [y for x,y in voter_points.values()])
                # plt.show()

                history = []
                for _ in range(num_rounds):
                    cand_points = generate_2d_points(cands, candpointmode,
                                                     sigma)
                    prof = profiles.approvalprofile_from_2d_euclidean(
                        voters,
                        cands,
                        voter_points,
                        cand_points,
                        approval_threshold)
                    history.append(prof)
                instances[str(spec)].append(history)

            print("writing instances to", picklefile)
            with open(picklefile, 'wb') as f:
                pickle.dump(instances[str(spec)], f, protocol=2)
        else:
            print("loading instances from", picklefile)
            with open(picklefile, 'rb') as f:
                instances[str(spec)] = pickle.load(f)

    return instances


random.seed(31415)

exp_specs = [
    [10000, 20, 5, 20, 0.2, "eucl2", "uniform_square", 1.5]]

instances = generate_instances(exp_specs)

rules = experiments.rules

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

    picklefile = "pickle/computation-" + name + ".pickle"
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
