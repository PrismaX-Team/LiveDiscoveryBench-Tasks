"""Final scoring template; replace before task review.

Framework arguments: --input <dir> --submission <dir> --result <json>.
Score the frozen submission offline and deterministically. The framework
provides the same run-local VerifyContext as validation. CI never runs this.
"""

import argparse


def main():
    parser = argparse.ArgumentParser()
    for name in ("input", "submission", "result"):
        parser.add_argument("--" + name, required=True)
    parser.parse_args()
    raise NotImplementedError("Implement task-specific final scoring")


if __name__ == "__main__":
    main()
