import re

from gurobi_logtools.parsers.util import float_pattern, typeconvert_groupdict


class NoRelParser:
    norel_log_start = re.compile(r"Starting NoRel heuristic")
    norel_primal_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )
    # the nodelog-ish line produced when running NoRel in a continued optimization:
    norel_primal_continuation_regex = re.compile(
        r"H\s*\d+\s+\d+\s+(?P<Incumbent>({0}|-))\s+(?P<BestBd>{0})\s+{0}%\s+(-|{0})\s+(?P<Time>\d+)s".format(
            float_pattern
        )
    )

    # Order is important in this list as regexes are checked in order
    norel_elapsed = [
        re.compile(
            r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s\s\(best\sbound\s(?P<BestBd>[^\s]+)[\)|,.*]"
        ),
        re.compile(r"Elapsed time for NoRel heuristic:\s(?P<Time>\d+)s"),
    ]

    norel_finished_regex = re.compile("NoRel heuristic complete")

    def __init__(self, continuation_parser):
        self._progress = []
        self._incumbent = None
        self._started = False
        self._finished = False
        self._continuation_parser = continuation_parser

    def get_summary(self) -> dict:
        """Return the summary based on the timeline information.

        It assumes that the best bound is always found in the last line, if exists.
        """
        if not self._progress:
            return {}
        last_log = self._progress[-1]
        result = {"NoRelTime": last_log["Time"]}
        if "BestBd" in last_log:
            result["NoRelBestBd"] = last_log["BestBd"]
        if self._incumbent is not None:
            result["NoRelBestSol"] = self._incumbent
        return result

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary and progress data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        if self._finished:
            return False

        if not self._started:
            match = self.norel_log_start.match(line)
            if match:
                self._started = True
                return True
            return False

        match = self.norel_primal_regex.match(line)
        if match:
            self._incumbent = float(match.group("Incumbent"))
            return True

        match = self.norel_primal_continuation_regex.match(line)
        if match and self._continuation_parser.activated:
            entry = typeconvert_groupdict(match)
            self._progress.append(entry)
            return True

        for regex in self.norel_elapsed:
            match = regex.match(line)
            if match:
                entry = typeconvert_groupdict(match)
                if self._incumbent is not None:
                    entry["Incumbent"] = self._incumbent
                self._progress.append(entry)
                return True

        match = self.norel_finished_regex.match(line)
        if match:
            self._finished = True
            return True

        # if self._started and not self._finished:
        #     return True

        return False

    def get_progress(self) -> list:
        """Return the progress of the norel heuristic."""
        return self._progress
