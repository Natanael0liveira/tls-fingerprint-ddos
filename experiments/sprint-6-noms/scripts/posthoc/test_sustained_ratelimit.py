"""Regression checks for bot identity, filter timing and replay validation; no private data."""
import copy
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

import sustained_ratelimit as replay


class SustainedReplayTests(unittest.TestCase):
    def setUp(self):
        self.day = pd.Timestamp("2026-10-01", tz="UTC")
        self.profile = pd.Series(1 / 40, index=[f"known_{i:02d}" for i in range(40)])
        self.profile.attrs["n"] = 10000
        self.clean = pd.Series({"known_00": 100})
        recs = [{"window": self.day - pd.Timedelta(days=1) + i * replay.STEP,
                 "clean": self.clean.copy(), "n": 100} for i in range(60)]
        recs += [{"window": self.day + i * replay.STEP,
                  "clean": self.clean.copy(), "n": 100} for i in range(15)]
        self.state = patch.dict(replay.G, {"recs": {"test-endpoint": recs}}, clear=True)
        self.state.start()
        self.addCleanup(self.state.stop)
        self.preparation = patch.object(replay, "prepare", return_value=(
            self.profile, frozenset({"known_00"}), -8.0, 110.0,
            pd.Series({"known_00": 100}), 100.0))
        self.preparation.start()
        self.addCleanup(self.preparation.stop)
        self.config = patch.object(replay, "CONFIGS", [("fresh", "A", 100)])
        self.config.start()
        self.addCleanup(self.config.stop)

    def run_task(self, assignment):
        with patch.object(replay, "ASSIGNMENT", assignment):
            return replay.task(("prospective", self.day.date(), "test-endpoint"))["attack"]["fresh:A100"]

    def test_fixed_bots_keep_their_fingerprints_across_windows(self):
        observed = []
        original = replay.picks

        def record(total, n, *args):
            if n == 200:
                observed.append(total[total.index.str.startswith("bot_")].copy())
            return original(total, n, *args)

        with patch.object(replay, "picks", side_effect=record):
            result = self.run_task("fixed")
        self.assertEqual(len(observed), 15)
        self.assertEqual(observed[0].sum(), 100)
        for counts in observed[1:]:
            pd.testing.assert_series_equal(observed[0], counts)
        self.assertEqual(result["windows"][0]["deployed_primary"], 0)
        self.assertGreater(result["windows"][1]["deployed_primary"], 0)

    def test_resampled_mode_preserves_original_random_stream(self):
        observed = []
        original = replay.botnet

        def record(*args):
            bot, pairs = original(*args)
            observed.append(bot.copy())
            return bot, pairs

        with patch.object(replay, "botnet", side_effect=record):
            self.run_task("resampled")
        rng = np.random.default_rng([replay.SEED, self.day.date().toordinal(),
                                     replay.zlib.crc32(b"test-endpoint"), 0])
        stacks = replay.stacks_for("fresh", 25, self.profile, rng)
        self.assertEqual(len(observed), 15)
        for actual in observed:
            expected, _ = original(100, stacks, replay.ARGS, rng)
            pd.testing.assert_series_equal(actual, expected)
        self.assertTrue(any(not observed[0].equals(x) for x in observed[1:]))

    def test_filters_start_next_window_and_expire_after_one_hour(self):
        count = 0

        def select_once(total, n, *args):
            nonlocal count
            if n == 100:
                return frozenset(), frozenset()
            count += 1
            return frozenset(), frozenset({"bot_stack_000"}) if count == 1 else frozenset()

        with patch.object(replay, "picks", side_effect=select_once), patch.object(
                replay, "botnet", return_value=(pd.Series({"bot_stack_000": 100}), 0)):
            result = self.run_task("fixed")
        coverage = [w["deployed_primary"] for w in result["windows"]]
        self.assertEqual(coverage, [0.0] + [1.0] * 12 + [0.0] * 2)
        self.assertAlmostEqual(result["D6"][0], 5 / 6)
        self.assertAlmostEqual(result["D12"][0], 11 / 12)
        self.assertTrue(all(x == 0 for x in result["D12"][1:]))

    def test_cap_challenges_only_excess_with_proportional_exposure(self):
        legit, bots, acted = replay.rate_limit(pd.Series({"shared": 6, "new": 0}),
            pd.Series({"shared": 4, "new": 5}), pd.Series({"shared": 8}))
        self.assertTrue(acted)
        self.assertAlmostEqual(legit, 1.2)
        self.assertAlmostEqual(bots, 1.8)

    def test_matching_clean_replay_is_accepted(self):
        replay.require_validated({"prospective": self.valid_check()})

    @staticmethod
    def valid_check():
        return {"mismatched": {"windows": 0, "trigger": 0, "picks": 0},
                "max_abs_collateral_difference": 0.0,
                "false_alarms_rebuilt": 31, "false_alarms_stored": 31}

    def test_mismatch_blocks_result_publication(self):
        for key in ("windows", "trigger", "picks", "collateral", "false_alarms", "nan"):
            with self.subTest(key=key):
                check = copy.deepcopy(self.valid_check())
                if key in check["mismatched"]:
                    check["mismatched"][key] = 1
                elif key == "collateral":
                    check["max_abs_collateral_difference"] = 0.01
                elif key == "nan":
                    check["max_abs_collateral_difference"] = float("nan")
                else:
                    check["false_alarms_rebuilt"] = 30
                with self.assertRaises(ValueError):
                    replay.require_validated({"prospective": check})


if __name__ == "__main__":
    unittest.main()
