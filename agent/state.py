import json
import hashlib


class CTFState:

    def __init__(self):

        self.actions = []

        self.results = []

        self.flags = []

        self.observations = []

    # ==========================================
    # ACTION TRACKING
    # ==========================================

    def action_already_done(
        self,
        tool,
        arguments,
    ):

        for action in self.actions:

            if (
                action["tool"] == tool
                and action["arguments"] == arguments
            ):
                return True

        return False

    def add_action(
        self,
        tool,
        arguments,
    ):

        self.actions.append({
            "tool": tool,
            "arguments": arguments,
        })

    # ==========================================
    # RESULT TRACKING
    # ==========================================

    def process_result(
        self,
        tool,
        arguments,
        result,
    ):

        self.add_action(
            tool,
            arguments,
        )

        self.results.append({
            "tool": tool,
            "arguments": arguments,
            "result": result,
        })

        self._extract_observations(
            result
        )

    # ==========================================
    # OBSERVATIONS
    # ==========================================

    def _extract_observations(
        self,
        result,
    ):

        if not isinstance(result, dict):
            return

        if result.get("stdout"):

            self.observations.append(
                result["stdout"]
            )

        if result.get("title"):

            self.observations.append(
                f"HTTP title: {result['title']}"
            )

        if result.get("status"):

            self.observations.append(
                f"HTTP status: {result['status']}"
            )

        if result.get("interesting_paths"):

            for item in result[
                "interesting_paths"
            ]:

                self.observations.append(
                    f"Interesting path: "
                    f"{item}"
                )

    # ==========================================
    # FLAGS
    # ==========================================

    def add_flag(
        self,
        flag,
    ):

        if flag not in self.flags:

            self.flags.append(
                flag
            )

    # ==========================================
    # SUMMARY
    # ==========================================

    def summary(self):

        return {
            "actions": self.actions,
            "observations": self.observations[
                -20:
            ],
            "flags": self.flags,
            "result_count": len(
                self.results
            ),
        }

    # ==========================================
    # SERIALIZATION
    # ==========================================

    def to_json(self):

        return json.dumps(
            self.summary(),
            indent=2,
            default=str,
        )
