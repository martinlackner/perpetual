# Example that loads profiles from files.

# Author: Benjamin Krenn

import file_loader
import perpetual_rules as perpetual

print "soi data from data folder"
approval_profiles, voters = file_loader.start_tsoi_load("data/", 10, from_date="20170309", to_date="20170316")
weights = perpetual.init_weights("per_quota", voters)
for approval_profile in approval_profiles:
	print "Perpetual Quota selects", perpetual.per_quota(approval_profile, weights)


print "Spotify csv data"
approval_profiles, voters = file_loader.start_spotify_csv_load("spotify/", 0.7,
															   from_date="20161230", to_date="20161230")
weights = perpetual.init_weights("per_quota", voters)
for approval_profile in approval_profiles:
	print "Perpetual Quota selects", perpetual.per_quota(approval_profile, weights)
