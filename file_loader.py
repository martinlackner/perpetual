# Loads approval profiles from tsoi files

# Author: Benjamin Krenn


import profiles
import os


script_dir = os.path.dirname(__file__)


# Loads all tsoi files directly within the given directory.
def start_tsoi_load(dir_name, max_approvals=None):

	input_path = os.path.join(script_dir, dir_name)
	files = []
	file_dir = None
	for (dir_path, _, filenames) in os.walk(input_path):
		file_dir = dir_path
		files = filenames
		break
	approval_profiles = []
	all_voters = set()
	if file_dir is not None:
		files = sorted(files)  # sorts from oldest to newest if name is sortable by date (YYYYMMDD)
		for f in files:
			if f.endswith('.tsoi'):
				candidates, profile = load_tsoi_file(
					os.path.join(file_dir, f), max_approvals)
				approval_profiles.append(profiles.ApprovalProfile(
					list(profile.keys()), candidates, profile))
				all_voters = all_voters.union(list(profile.keys()))

	return approval_profiles, all_voters


# Loads the given file.
# Only considers up to max_approvals alternatives per voter.
# If no max_approvals is given it takes 50% of the alternatives (at least one).
def load_tsoi_file(abs_path, max_approvals):
	with open(abs_path, "r") as f:
		lines = f.readlines()
		candidate_count = int(lines[0])
		after_candidates = candidate_count + 1
		candidates = []
		for line in lines[1:after_candidates]:
			split_line = line.split(',')[1:]
			joined_line = ','.join(split_line)
			candidates.append(joined_line.strip())
		profile = {}
		rankings_count = int(lines[after_candidates].split(',')[1])
		last_ranking_line = after_candidates + 1 + rankings_count
		used_candidates = set()
		for line in lines[after_candidates + 1: last_ranking_line + 1]:
			parts = line.split(':')
			if len(parts) != 2:
				print("####### ERROR #######")
				print("ranking Data seems to have wrong format in file %s" % abs_path)
			local_ranking = []
			profile[parts[0]] = local_ranking  # name of the voter
			if max_approvals is None:
				take = max(len(parts[1].split(',')[1:]) / 2, 1)
			else:
				take = max_approvals
			for vote in parts[1].split(',')[1:]:  # the first number is a count, this can be ignored here
				if take > 0:
					take -= 1
					local_ranking.append(int(vote))
					used_candidates.add(int(vote))
				else:
					break

		return list(used_candidates), profile


# This loads csv files with spotify charts and returns a list of approval profiles
# and a list of all voters from  these profiles
def start_spotify_csv_load(dir_name, max_approval_percent=0.8):
	input_path = os.path.join(script_dir, dir_name)
	files = []
	file_dir = None
	for (dir_path, _, filenames) in os.walk(input_path):
		file_dir = dir_path
		files = filenames
		break
	approval_profiles = []
	all_voters = set()
	candidates = set()
	profile = {}
	if file_dir is not None:
		files = sorted(files)  # sorts from oldest to newest if name is sortable by date (YYYYMMDD)
		date = None
		for f in files:
			file_date = f.split("_")[1]  # date should be between first and second "_"
			if f.endswith('.csv'):
				if date is None or file_date != date:
					if len(profile) > 0:
						profiles.ApprovalProfile(list(profile.keys()), candidates, profile)
						approval_profiles.append(profiles.ApprovalProfile(
							list(profile.keys()), candidates, profile))
						all_voters = all_voters.union(list(profile.keys()))
					profile = {}
					date = file_date
					candidates = set()
				load_spotify_csv_file(os.path.join(file_dir, f),
									  candidates, profile, max_approval_percent)
	if len(profile) > 0:
		profiles.ApprovalProfile(list(profile.keys()), candidates, profile)
		approval_profiles.append(profiles.ApprovalProfile(
			list(profile.keys()), candidates, profile))
		all_voters = all_voters.union(list(profile.keys()))
	return approval_profiles, all_voters


# Opens a given spotify csv file.
# All the used candidates are added to the set used_candidates.
# All alternatives that reached at least highest_streaming_number * max_approval_percent streams
# are added to the profile for the given voter
def load_spotify_csv_file(abs_path, used_candidates, profile, max_approval_percent):
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
						minimum_streams = float(x[-4]) * max_approval_percent
						profile[voter] = []
					alternative_id = x[-1].strip()
					streams = float(x[-4])
					if streams < minimum_streams:
						break
					profile[voter].append(alternative_id)
					used_candidates.add(alternative_id)
