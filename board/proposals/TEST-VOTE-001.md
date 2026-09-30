# [TEST] SCAP-NG Board Voting Integration

> **TEST ONLY — NOT AN OFFICIAL BOARD VOTE.** This discussion may be deleted after connectivity testing.

## Proposed decision

Do you agree with using GitHub Discussions and reactions as the mechanism for recording future SCAP-NG OVAL Board votes, subject to an approved voting procedure?

## Background

The SCAP-NG effort has a backlog of architecture and compatibility questions requiring documented OVAL Board decisions. Each future voting discussion should contain one clearly phrased proposal, technical rationale, alternatives, compatibility implications, and links to specification changes.

This temporary proposal verifies that a GitHub Action can publish a prewritten Markdown proposal as a Discussion. It also provides a place to test whether authorized tooling can subsequently retrieve individual reaction identities.

## Test reactions

- 👍 (`+1`): Yes
- 👎 (`-1`): No
- 👀 (`eyes`): Abstain

**These symbols are provisional test conventions.** The OVAL Board has not yet approved official voting rules, member eligibility, quorum, duration, or handling of changed/multiple reactions.

## Acceptance criteria

1. This discussion is created from a Markdown file by GitHub Actions.
2. A subsequent run finds this discussion and does not create a duplicate.
3. A board member adds a reaction.
4. We check whether reaction type and GitHub username are available from the API.
5. No actual specification decision is inferred from this test.

<!-- scap-ng-proposal-id: TEST-VOTE-001 -->
