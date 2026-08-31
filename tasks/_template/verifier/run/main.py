"""Fixed verifier entry-point template.

Repository automation checks only that this file exists and is non-empty. It never
imports or executes pull-request code. Replace this module with the task's offline,
deterministic verifier after the project-wide invocation contract is finalized.
"""


def main() -> None:
    raise NotImplementedError("Replace the verifier template before review")


if __name__ == "__main__":
    main()
