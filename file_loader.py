# Loads approval profiles from tsoi files

# Author: Benjamin Krenn


import profiles
import os

script_dir = os.path.dirname(__file__)


# Loads all tsoi files directly within the given directory.
# All tsoi files should conform to the naming convention
# of *_date.tsoi where the date format should be sortable
# from_date and to_date are strings that state the first
# file to consider and the last one.
def start_tsoi_load(dir_name, threshold=None,
                    from_date=None, to_date=None, only_complete=False,
                    with_weights=False):
    file_dir, files = get_file_names(dir_name)

    approval_profiles = []
    all_voters = set()
    if file_dir is not None:
        # sorts from oldest to newest if name is sortable by date
        # (YYYYMMDD)
        files = sorted(files)
        for f in files:
            if f.endswith('.tsoi'):
                if from_date is not None or to_date is not None:
                    date = f.split("_")[-1].split(".tsoi")[0]
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


# Loads the given file.
# Only considers up to max_approvals alternatives per voter.
# If no max_approvals is given it takes 50% of the alternatives
# (at least one).
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
    max_weight = get_weigth(ranking[0])
    for vote in ranking:
        if get_weigth(vote) >= max_weight * threshold:
            add_candidate(vote, appr_set)


def get_weigth(rank):
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
                appr_set.append(c.strip())
        else:
            appr_set.append(candidate)
    else:
        raise Exception("Invalid format.", rank)


def get_ranking_without_weights(line, appr_set, threshold):
    ranking = line.split(',')[1:]
    if threshold is None:
        threshold = max(len(ranking) / 2, 1)

    if len(ranking) == 0:
        return
    for vote in ranking:
        if threshold > 0:
            add_candidate(vote, appr_set)
            threshold -= 1
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
        raise Exception("No files found in ", dir_name)
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



# This loads csv files with spotify charts and returns a list of
# approval profiles
# and a list of all voters from  these profiles
# from_date and to_date are strings that state the first file to
# consider and the last one.
def start_spotify_csv_load(dir_name, approval_percent=0.8,
                           from_date=None, to_date=None,
                           only_complete=False):
    file_dir, files = get_file_names(dir_name)

    approval_profiles = []
    all_voters = set()
    candidates = set()
    profile = {}
    if file_dir is not None:
        files = sorted(
            files)  # sorts from oldest to newest if name is sortable
        # by date (YYYYMMDD)
        date = None
        for f in files:
            file_date = f.split("_")[
                1]  # date should be between first and second "_"
            if f.endswith('.csv'):
                if from_date is not None or to_date is not None:
                    if from_date is not None and file_date < from_date:
                        continue
                    if to_date is not None and file_date > to_date:
                        break
                if date is None or file_date != date:
                    if len(profile) > 0:
                        profiles.ApprovalProfile(list(profile.keys()),
                                                 candidates, profile)
                        approval_profiles.append(
                            profiles.ApprovalProfile(
                                list(profile.keys()), candidates,
                                profile))
                        all_voters = all_voters.union(
                            list(profile.keys()))
                    profile = {}
                    date = file_date
                    candidates = set()
                load_spotify_csv_file(os.path.join(file_dir, f),
                                      candidates, profile,
                                      approval_percent)
    if len(profile) > 0:
        profiles.ApprovalProfile(list(profile.keys()), candidates,
                                 profile)
        approval_profiles.append(profiles.ApprovalProfile(
            list(profile.keys()), candidates, profile))
        all_voters = all_voters.union(list(profile.keys()))
    if only_complete:
        approval_profiles, all_voters = \
            remove_additional_voters(approval_profiles, all_voters)
    return approval_profiles, all_voters


# Opens a given spotify csv file.
# All the used candidates are added to the set used_candidates.
# All alternatives that reached at least highest_streaming_number *
# max_approval_percent streams
# are added to the profile for the given voter
def load_spotify_csv_file(abs_path, used_candidates, profile,
                          approval_percent):
    with open(abs_path, "r") as f:
        lines = f.readlines()
        if len(lines) > 1:
            if not lines[1].startswith('NA,NA,'):
                minimum_streams = None
                voter = None
                for line in lines[1:]:
                    x = line.split(",")
                    if voter is None:
                        voter = x[-2]
                        minimum_streams = float(
                            x[-4]) * approval_percent
                        profile[voter] = []
                    alternative_id = x[-1].strip()
                    streams = float(x[-4])
                    if streams < minimum_streams:
                        break
                    profile[voter].append(alternative_id)
                    used_candidates.add(alternative_id)



