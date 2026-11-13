# PR review evaluation protocol

## Minimum pilot: three real pull requests

Choose a representative set from the connected TIKVARON repository:

1. Small bug fix with a known expected outcome and tests.
2. Multi-file feature or behavior change.
3. Security-sensitive change involving auth, validation, persistence, secrets, or external inputs.

Run the same commit through the reviewer and record base/head SHAs. Have a maintainer independently review each diff before inspecting AI findings.

## Score each finding

Record true positives, false positives, severity calibration, changed-file/line accuracy, actionability, runtime, model/token usage, and cost. Recall requires an independently established set of known defects; do not report recall when there is no ground-truth defect set.

## Acceptance

- Findings reference actual changed paths and valid diff lines.
- Secret or PR-head code is never exposed to a privileged workflow.
- Failed/incomplete model responses fail the job rather than publish partial analysis.
- PR state is unchanged by the live pilot.
- Human reviewers score every finding before any merge-blocking behavior is considered.

No merge gate is enabled by default.
