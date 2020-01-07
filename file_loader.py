# Loads approval profiles from tsoi files

# Author: Benjamin Krenn


import profiles
import os

script_dir = os.path.dirname(__file__)


def start_tsoi_load(dir_name, threshold=None,
                    from_date=None, to_date=None, only_complete=False,
                    with_weights=False):
    """
    Loads all tsoi and ttoi files directly within the given directory.
    All tsoi and ttoi files should conform to the naming convention
    of *_date.tsoi or *_date.ttoi where the date format should
    be sortable.


    Parameters
    ----------
    dir_name : str
        Relative path to the directory with the files. (root of module).

    threshold : int or float
        An int for with_weights=False means up to the rank threshold.

        A float for with_weights=True means at least a weight of
            max_weight * threshold needs to be reached within a ranking.

        Or None for default cases: with weights 0.9 without 50%

    from_date: str
        Date in the same format as in the filenames. Files before this
            date are ignored.

    to_date: str
        Date in the same format as in the filenames. Files after this
            date are ignored.

    only_complete: Boolean
        if True all voters that are not within all profiles are removed.

    with_weights: Boolean
        States if weights are used to decide on the approval set.
    Returns
    -------
    list, list
        A list of ApprovalProfiles.
        A list of all voters.


    from_date and to_date are strings that state the first
    file to consider and the last one.

    """
    file_dir, files = get_file_names(dir_name)

    approval_profiles = []
    all_voters = set()
    if file_dir is not None:
        # sorts from oldest to newest if name is sortable by date
        # (YYYYMMDD)
        files = sorted(files)
        for f in files:
            if f.endswith(".tsoi") or f.endswith(".ttoi"):
                if from_date is not None or to_date is not None:
                    date = f.split("_")[-1].split(".t")[0]
                    if from_date is not None and date < from_date:
                        continue
                    if to_date is not None and date > to_date:
                        break
                candidates, profile = load_file(
                    os.path.join(file_dir, f), threshold, with_weights)
                approval_profiles.append(profiles.ApprovalProfile(
                    list(profile.keys()), candidates, profile))
                all_voters = all_voters.union(list(profile.keys()))
    if only_complete:
        approval_profiles, all_voters = \
            remove_additional_voters(approval_profiles, all_voters)
    if len(approval_profiles) == 0 or len(all_voters) == 0:
        raise Exception("No data found in", dir_name)
    return approval_profiles, all_voters


def load_file(abs_path, threshold, with_weights):
    with open(abs_path, "r") as f:
        lines = f.readlines()
        candidate_count = int(lines[0])
        after_candidates = candidate_count + 1
        # candidates = {}
        # for line in lines[1:after_candidates]:
        #     split_line = line.split(',')
        #     id = split_line[0].strip()
        #     split_line = split_line[1:]
        #     joined_line = ','.join(split_line)
        #     candidates[id] = joined_line.strip()
        profile = {}
        rankings_count = int(lines[after_candidates].split(',')[1])
        last_ranking_line = after_candidates + 1 + rankings_count
        used_candidates = set()
        for line in lines[after_candidates + 1: last_ranking_line + 1]:
            parts = line.split(':')
            if len(parts) != 2:
                print("####### ERROR #######")
                print("ranking Data seems to have wrong format in "
                      "file",
                      abs_path)
            local_ranking = []
            profile[parts[0]] = local_ranking  # name of the voter
            if with_weights:
                get_ranking_with_weights(parts[1], local_ranking,
                                         threshold)
            else:
                get_ranking_without_weights(parts[1], local_ranking,
                                            threshold)
            for candidate in local_ranking:
                used_candidates.add(candidate)

        return list(used_candidates), profile


def get_ranking_with_weights(line, appr_set, threshold):
    if threshold is None:
        threshold = 0.9
    ranking = line.split(',')[1:]
    if len(ranking) == 0:
        return

    max_weight = None
    tied = False
    curr_voters = ""
    for i in range(len(ranking)):
        voter = ranking[i].strip()
        if not tied:
            if voter.startswith("{"):
                tied = True
                curr_voters = voter
                if "}" in voter:
                    raise Exception("Single voter in {} is invalid")
            else:
                if max_weight is None:
                    max_weight = get_weight(voter)
                if get_weight(voter) >= max_weight * threshold:
                    add_candidate(voter, appr_set)
                else:
                    break
        else:
            curr_voters += "," + voter
            if "}" in voter:
                if max_weight is None:
                    max_weight = get_weight(curr_voters)
                if get_weight(curr_voters) >= max_weight * threshold:
                    add_candidate(curr_voters, appr_set)
                    curr_voters = ""
                else:
                    break
            else:
                continue


def get_weight(rank):
    parts = rank.split("[")
    if len(parts) != 2:
        raise Exception("Invalid format for with weights")
    else:
        weight = float(parts[1].split("]")[0])
    return weight


def add_candidate(rank, appr_set):
    parts = rank.split("[")
    if 0 < len(parts) < 3:
        candidate = parts[0].strip()
        if candidate.find("{") != -1:
            if candidate[0] != "{" or candidate[-1] != "}":
                raise Exception("Invalid format for tied candidates.",
                                rank)
            candidates = candidate[1:-1].split(",")
            for c in candidates:
                appr_set.append(int(c.strip()))
        else:
            appr_set.append(int(candidate))
    else:
        raise Exception("Invalid format.", rank)


def get_ranking_without_weights(line, appr_set, threshold):
    ranking = line.split(',')[1:]
    if threshold is None:
        threshold = max(len(ranking) / 2, 1)

    if len(ranking) == 0:
        return

    tied = False
    curr_voters = ""
    for i in range(len(ranking)):
        if threshold > 0:
            voter = ranking[i].strip()
            if not tied:
                if voter.startswith("{"):
                    tied = True
                    # count = 1
                    curr_voters = voter
                    if "}" in voter:
                        raise Exception("Single voter in {} is invalid")
                else:
                    add_candidate(voter, appr_set)
                    threshold -= 1
            else:
                curr_voters += "," + voter
                # count += 1
                if "}" in voter:
                    add_candidate(curr_voters, appr_set)
                    curr_voters = ""
                    threshold -= 1  # or -= count
                    # count = 0
                else:
                    continue
        else:
            break


def get_file_names(dir_name):
    input_path = os.path.join(script_dir, dir_name)
    files = []
    file_dir = None
    for (dir_path, _, filenames) in os.walk(input_path):
        file_dir = dir_path
        files = filenames
        break
    if file_dir is None or len(files) == 0:
        raise Exception("No files found in ", input_path)
    return file_dir, files


def remove_additional_voters(approval_profiles, all_voters):
    """Generates a list of profiles that all have exactly the same
    voters."""
    voters = set(all_voters)
    for profile in approval_profiles:
        voters = voters.intersection(profile.voters)
    if len(voters) == len(all_voters):
        return approval_profiles, all_voters

    voter_list = list(voters)
    appr_profiles = []
    for profile in approval_profiles:
        if len(profile.voters) == len(voters):
            appr_profiles.append(profile)
        else:
            appr_set = {}
            cands = set()
            for voter, appr in profile.approval_sets.items():
                if voter in voters:
                    appr_set[voter] = appr
                    cands = cands.union(appr)
            appr_profiles.append(profiles.ApprovalProfile(voter_list,
                                                          list(cands),
                                                          appr_set))
    return appr_profiles, voters




