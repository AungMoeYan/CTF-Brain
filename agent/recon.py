class ReconStrategy:

    def __init__(self, state):

        self.state = state

    def prompt_context(self):

        summary = self.state.summary()

        actions = summary.get(
            "actions",
            [],
        )

        observations = summary.get(
            "observations",
            [],
        )

        flags = summary.get(
            "flags",
            [],
        )

        if flags:

            return """
A flag has already been discovered.

Do not perform unnecessary additional
enumeration. Prepare the final answer.
"""

        if not actions:

            return """
No reconnaissance has been performed yet.

Choose the most appropriate first
reconnaissance action based on the user's
question.

For network targets, Nmap is usually the
best first step.

For an explicitly supplied HTTP URL,
web_enum is usually appropriate.
"""

        return f"""
Previous actions:

{actions}

Recent observations:

{observations}

Use these observations to decide the
next most useful action.

Avoid repeating the same tool with the
same arguments.

Prefer information-gathering actions that
reduce uncertainty about the target.
"""
