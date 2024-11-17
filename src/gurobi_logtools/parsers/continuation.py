import re

from gurobi_logtools.parsers.nodelog import NodeLogParser

class DummyContinuationParser:

    activated=True

    def has_buffer(self):
        return False


class ContinuationParser:

    MAX_BUFFER=1
    _NodeLogParser = NodeLogParser

    continuation_regex = re.compile(
        r"Continuing optimization..."
    )

    norel_start_regex = re.compile("Starting NoRel heuristic")

    def __init__(self):
        self.activated = False
        self._lines_buffered = 0
        self._pretree_parser = None
        self._nodelogbuffer = self._NodeLogParser(DummyContinuationParser())

    def register_pretree_parser(self, pretree_parser):
        self._pretree_parser = pretree_parser

    def parse(self, line: str) -> bool:
        """Parse the given log line to populate summary data.

        Args:
            line (str): A line in the log file.

        Returns:
            bool: Return True if the given line is matched by some pattern.
        """
        match = self.continuation_regex.match(line)
        if match:
            self.activated=True
            return True
        
        if self.activated:
            match = self.norel_start_regex.match(line)
            if match:
                progress = self.take_progress()
                if self._pretree_parser:
                    self._pretree_parser.receive_progress(progress)
                return False

            if self._lines_buffered == self.MAX_BUFFER:
                return False
            match = self._nodelogbuffer.parse(line)
            if match:
                self._lines_buffered += 1
                return True

        return False

    def get_summary(self) -> dict:
        """Return the current parsed summary."""
        return {"Continuation": self.activated}

    def remove_buffer(self):
        self._nodelogbuffer = None

    def has_buffer(self):
        return self._nodelogbuffer is not None

    def take_progress(self) -> list: 
        """Return the progress of the search tree."""
        if self.has_buffer():
            return []
        progress = self._nodelogbuffer._progress
        self.remove_buffer()
        return progress