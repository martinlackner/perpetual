# Loads approval profiles from tsoi files

# Author: Benjamin Krenn


import profiles
import os


script_dir = os.path.dirname(__file__)


def start(dir_name, max_approvals=None):

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
		print files
		for f in files:
			if f.endswith('.tsoi'):
				candidates, profile = load_tsoi_file(
					os.path.join(file_dir, f), max_approvals)
				approval_profiles.append(profiles.ApprovalProfile(
					list(profile.keys()), candidates, profile))
				all_voters = all_voters.union(list(profile.keys()))

	return approval_profiles, all_voters


def load_tsoi_file(abs_path, max_apporvals):
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
			if max_apporvals is None:
				take = max(len(parts[1].split(',')[1:]) / 2, 1)
			else:
				take = max_apporvals
			for vote in parts[1].split(',')[1:]:  # the first number is a count, this can be ignored here
				if take > 0:
					take -= 1
					local_ranking.append(int(vote))
					used_candidates.add(int(vote))
				else:
					break

		return list(used_candidates), profile

