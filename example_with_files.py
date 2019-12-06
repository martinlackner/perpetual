# Example that loads profiles from files.

# Author: Benjamin Krenn

import file_loader
import perpetual_rules as perpetual

approval_profiles, voters = file_loader.start("data/")
weights = perpetual.init_weights("per_quota", voters)
for approval_profile in approval_profiles:
	print "Perpetual Quota selects", perpetual.per_quota(approval_profile, weights)