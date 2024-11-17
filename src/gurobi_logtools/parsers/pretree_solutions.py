import re

from gurobi_logtools.parsers.util import float_pattern, typeconvert_groupdict


class PreTreeSolutionParser:
    pretree_solution_regex = re.compile(
        r"Found heuristic solution:\sobjective\s(?P<Incumbent>[^\s]+)"
    )

    pretree_solution_continuation_regex = re.compile(
        r"H\s*\d+\s+\d+\s+(?P<Incumbent>{0})\s+{0}\s+{0}%\s+(-|{0})\s+\d+s".format(
            float_pattern
        )
    )

    def __init__(self, continuation_parser):
        """Initialize the pre-tree solutions parser (does not include NoRel solutions).

        The PresolveParser extends beyond the lines associated with the presolved
        model. Specifically, it includes information for all lines appearing between
        the HeaderParser and the NoRelParser or the RelaxationParser.
        """
        self._progress = []
        self._summary = {}
        self._continuation_parser = continuation_parser
        continuation_parser.register_pretree_parser(self)
        # self._started = False

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        if self._continuation_parser.activated:
            match = self.pretree_solution_continuation_regex.match(line)
            if match:
                self._progress.append(typeconvert_groupdict(match))
                return True

        match = self.pretree_solution_regex.match(line)
        if match:
            self._progress.append(typeconvert_groupdict(match))
            return True
        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return {"PreTreeSolutions": len(self._progress)}

    def get_progress(self) -> list:
        """Return the progress of the search tree."""
        return self._progress

    def receive_progress(self, progress):
        self._progress.extend([{"Incumbent": p["Incumbent"]} for p in progress])
