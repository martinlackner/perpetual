# Unit tests

# Author: Martin Lackner


import unittest

import file_loader
import perpetual_rules as perpetual
import profiles


class TestPerpetualRules(unittest.TestCase):

    def test_unitcost_fails_sp(self):
        rule = "per_unitcost"
        appsets = {1: [1], 2: [1], 3: [1],
                   4: [2], 5: [2], 6: [3]}
        voters = [1, 2, 3, 4, 5, 6]
        cands = [1, 2, 3]
        profile = profiles.ApprovalProfile(voters, cands, appsets)
        weights = perpetual.init_weights(rule, voters)

        expected_choices = [1, 2, 1, 1, 2, 1]
        for i in range(len(expected_choices)):
            choice = perpetual.compute_rule(rule, profile, weights)
            self.assertEqual(choice, expected_choices[i])

    def test_reset_fails_sp(self):
        rule = "per_reset"
        appsets = {1: [1], 2: [1], 3: [1],
                   4: [2], 5: [3], 6: [4]}
        voters = [1, 2, 3, 4, 5, 6]
        cands = [1, 2, 3, 4]
        profile = profiles.ApprovalProfile(voters, cands, appsets)
        weights = perpetual.init_weights(rule, voters)

        expected_choices = [1, 1, 1, 2, 1, 3]
        for i in range(len(expected_choices)):
            choice = perpetual.compute_rule(rule, profile, weights)
            self.assertEqual(choice, expected_choices[i])

    def test_av_fails_sp(self):
        rule = "av"
        appsets = {1: [1], 2: [1], 3: [2]}
        voters = [1, 2, 3]
        cands = [1, 2]
        profile = profiles.ApprovalProfile(voters, cands, appsets)
        weights = perpetual.init_weights(rule, voters)

        expected_choices = [1, 1, 1]
        for i in range(len(expected_choices)):
            choice = perpetual.compute_rule(rule, profile, weights)
            self.assertEqual(choice, expected_choices[i])

    def test_equality_fails_sp(self):
        rule = "per_equality"
        appsets = {1: [1], 2: [1], 3: [1], 4: [2]}
        voters = [1, 2, 3, 4]
        cands = [1, 2]
        profile = profiles.ApprovalProfile(voters, cands, appsets)
        weights = perpetual.init_weights(rule, voters)

        expected_choices = [1, 2, 1, 2]
        for i in range(len(expected_choices)):
            choice = perpetual.compute_rule(rule, profile, weights)
            self.assertEqual(choice, expected_choices[i])

    def test_av_has_dsg_infty(self):
        rule = "av"
        for k in [10, 20, 30]:
            start_dryspell = 0
            dryspell_voter = 3
            appsets = {1: [1], 2: [1], 3: [2]}
            voters = [1, 2, 3]
            cands = [1, 2]
            profile = profiles.ApprovalProfile(voters, cands, appsets)
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [1] * k
            for i in range(len(expected_choices)):
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[dryspell_voter])

    def test_pav_has_dsg_infty(self):
        rule = "per_pav"
        for k in [10, 20, 30]:
            start_dryspell = 2 * k
            dryspell_voter = 3
            appsets = []
            for _ in range(k):
                appsets.append({1: [1], 2: [2], 3: [1]})
                appsets.append({1: [1], 2: [2], 3: [2]})
            for _ in range(k):
                appsets.append({1: [1], 2: [1], 3: [3]})
            voters = [1, 2, 3]
            cands = [1, 2, 3]
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [1, 2] * k + [1] * k
            for i in range(len(expected_choices)):
                profile = profiles.ApprovalProfile(voters, cands, appsets[i])
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[i][dryspell_voter])

    def test_equality_has_dsg_infty(self):
        rule = "per_equality"
        for k in [10, 20, 30]:
            start_dryspell = 2 * k
            dryspell_voter = 1
            appsets = []
            for _ in range(2 * k):
                appsets.append({1: [1, 2], 2: [1], 3: [2]})
            for _ in range(2 * k):
                appsets.append({1: [1], 2: [2], 3: [3]})
            voters = [1, 2, 3]
            cands = [1, 2, 3]
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [1, 2] * k + [2, 3] * k
            for i in range(len(expected_choices)):
                profile = profiles.ApprovalProfile(voters, cands, appsets[i])
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[i][dryspell_voter])

    def test_unitcost_has_dsg_infty(self):
        rule = "per_unitcost"
        for k in [10, 20, 30]:
            start_dryspell = 0
            dryspell_voter = 6
            appsets = {1: [1], 2: [1], 3: [1],
                       4: [2], 5: [2], 6: [3]}
            voters = [1, 2, 3, 4, 5, 6]
            cands = [1, 2, 3]
            profile = profiles.ApprovalProfile(voters, cands, appsets)
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [1, 2, 1, 1, 2] * k
            for i in range(len(expected_choices)):
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[dryspell_voter])

    def test_nash_has_dsg_infty(self):
        rule = "per_nash"
        for k in [10, 20, 30]:
            start_dryspell = 2 * k
            dryspell_voter = 1
            appsets = []
            for _ in range(2 * k):
                appsets.append({1: [2, 3], 2: [2], 3: [3]})
            for _ in range(2 * k):
                appsets.append({1: [1], 2: [2], 3: [3]})
            voters = [1, 2, 3]
            cands = [1, 2, 3]
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [2, 3] * (2 * k)
            for i in range(len(expected_choices)):
                profile = profiles.ApprovalProfile(voters, cands, appsets[i])
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[i][dryspell_voter])

    def test_quota_has_dsg_infty(self):
        rule = "per_quota"
        for k in [10, 20, 30]:
            start_dryspell = 2 * k
            dryspell_voter = 1
            appsets = []
            for _ in range(2 * k):
                appsets.append({1: [2, 3], 2: [2], 3: [3]})
            for _ in range(k):
                appsets.append({1: [1], 2: [2], 3: [3]})
            voters = [1, 2, 3]
            cands = [1, 2, 3]
            weights = perpetual.init_weights(rule, voters)
            expected_choices = [2, 3] * (3 * k // 2)
            for i in range(len(expected_choices)):
                profile = profiles.ApprovalProfile(voters, cands, appsets[i])
                choice = perpetual.compute_rule(rule, profile, weights)
                self.assertEqual(choice, expected_choices[i])
                if i >= start_dryspell:
                    self.assertFalse(choice in appsets[i][dryspell_voter])

    def test_per_equality_tiebreaking(self):
        appsets1 = {1: [1], 2: [1], 3: [2], 4: [3]}
        appsets2 = {1: [1, 3], 2: [1], 3: [2], 4: [3]}
        voters = [1, 2, 3, 4]
        cands = [1, 2, 3, 4]
        profile1 = profiles.ApprovalProfile(voters, cands, appsets1)
        profile2 = profiles.ApprovalProfile(voters, cands, appsets2)
        weights = perpetual.init_weights("per_reset", voters)

        self.assertEqual(perpetual.per_equality(profile1, weights), 1)
        self.assertEqual(perpetual.per_equality(profile2, weights), 3)
        self.assertEqual(perpetual.per_equality(profile2, weights), 2)

    # test perpetual rules with a (very) simple instance
    def test_perpetualrules_simple(self):
        k = 6
        decision = {"av": [3]*k,
                    "per_pav": [3, 2, 3, 3, 2, 3],
                    "per_consensus": [3, 2, 3, 3, 2, 3],
                    "per_majority": [3, 3, 2, 3, 3, 3],
                    "per_unitcost": [3, 2, 3, 3, 2, 3],
                    "per_reset": [3, 2, 3, 2, 3, 2],
                    "per_nash": [3, 3, 2, 3, 2, 3],
                    "per_equality": [3, 2, 3, 2, 3, 2],
                    "per_phragmen": [3, 2, 3, 3, 2, 3],
                    "per_quota": [3, 2, 3, 3, 2, 3],
                    "per_quota_mod": [3, 2, 3, 3, 2, 3],
                    "per_2nd_prize": [3, 3, 2, 3, 3, 3]}

        self.longMessage = True

        appsets = {1: [3], 2: [3], 3: [2]}
        voters = [1, 2, 3]
        cands = [1, 2, 3, 4]
        profile = profiles.ApprovalProfile(voters, cands, appsets)

        for rule in perpetual.PERPETUAL_RULES:
            if rule == "serial_dictatorship" or rule == "random_dictatorship":
                continue

            weights = perpetual.init_weights(rule, voters)

            for i in range(k):
                self.assertEqual(perpetual.compute_rule(rule, profile,
                                                        weights),
                                 decision[rule][i],
                                 msg=rule + " failed in round " + str(i))
                if rule == "subtraction_numvoters":
                    self.assertEqual(sum(weights.values()), len(voters))

    # test perpetual rules on data from files
    def test_perpetualrules_simple_files(self):
        k = 6
        decision = {"av": [3]*6,
                    "per_pav": [3, 2, 3, 3, 2, 3],
                    "per_consensus": [3, 2, 3, 3, 2, 3],
                    "per_majority": [3, 3, 2, 3, 3, 3],
                    "per_unitcost": [3, 2, 3, 3, 2, 3],
                    "per_reset": [3, 2, 3, 2, 3, 2],
                    "per_nash": [3, 3, 2, 3, 2, 3],
                    "per_equality": [3, 2, 3, 2, 3, 2],
                    "per_phragmen": [3, 2, 3, 3, 2, 3],
                    "per_quota": [3, 2, 3, 3, 2, 3],
                    "per_quota_mod": [3, 2, 3, 3, 2, 3],
                    "per_2nd_prize": [3, 3, 2, 3, 3, 3]}

        self.longMessage = True

        approval_profiles, _ = file_loader.start_tsoi_load("unittests/simple")
        voters = approval_profiles[0].voters

        for rule in perpetual.PERPETUAL_RULES:
            if rule == "serial_dictatorship" or rule == "random_dictatorship":
                continue

            weights = perpetual.init_weights(rule, voters)
            i = 0
            for profile in approval_profiles:
                self.assertEqual(perpetual.compute_rule(rule, profile,
                                                        weights),
                                 decision[rule][i],
                                 msg=rule + " failed in round " + str(i))
                if rule == "subtraction_numvoters":
                    self.assertEqual(sum(weights.values()), len(voters))
                i += 1

    # test perpetual rules on more diverse data from files
    def test_perpetualrules_files(self):
        decision = {"av": [3, 1, 2, 1, 3, 2],
                    "per_pav": [3, 3, 2, 1, 3, 2],
                    "per_consensus": [3, 3, 2, 1, 1, 1],
                    "per_majority": [3, 3, 2, 1, 3, 2],
                    "per_unitcost": [3, 3, 2, 1, 3, 2],
                    "per_reset": [3, 3, 2, 1, 1, 2],
                    "per_nash": [3, 3, 2, 1, 3, 2],
                    "per_equality": [3, 3, 2, 1, 1, 2],
                    "per_phragmen": [3, 3, 2, 1, 1, 2],
                    "per_quota": [3, 3, 2, 1, 1, 2],
                    "per_quota_mod": [3, 3, 2, 1, 1, 2],
                    "per_2nd_prize": [3, 3, 2, 1, 3, 2]}

        self.longMessage = True

        approval_profiles, voters = file_loader.start_tsoi_load("unittests/diverse")
        self.assertEqual(len(voters), len(approval_profiles[0].voters),
                         msg="failed to read files, all profiles "
                             "should have equally many voters.")

        for rule in perpetual.PERPETUAL_RULES:
            if rule == "serial_dictatorship" or rule == "random_dictatorship":
                continue

            weights = perpetual.init_weights(rule, voters)
            for i, profile in enumerate(approval_profiles):
                self.assertEqual(perpetual.compute_rule(rule, profile,
                                                    weights),
                                 decision[rule][i],
                                 msg=rule + " failed in round " + str(i))
                if rule == "subtraction_numvoters":
                    self.assertEqual(sum(weights.values()), len(voters))


if __name__ == '__main__':
    unittest.main()
