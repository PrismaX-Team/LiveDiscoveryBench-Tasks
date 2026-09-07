"""Research feedback template; replace before task review.

Framework arguments: --input <dir> --request <json> --response <json>.
Define task-specific JSON feedback and budgets. The framework provides
VerifyContext.current() for shared run state. CI never executes this code.
"""

import argparse


def main():
    parser = argparse.ArgumentParser()
    for name in ("input", "request", "response"):
        parser.add_argument("--" + name, required=True)
    parser.parse_args()
    raise NotImplementedError("Implement task-specific feedback and budget rules")


if __name__ == "__main__":
    main()
