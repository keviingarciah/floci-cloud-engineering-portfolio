# Agent notes

This repository is a bilingual documentation index. The labs it points at live in other repositories. Do not create those applications here.

## Rules

- `projects/projects.yaml` is the source of truth. Read [projects/schema.en.md](projects/schema.en.md) before editing metadata.
- Keep English and Spanish documents equivalent. Product names stay in English. Do not ship a placeholder translation.
- Do not invent progress, test results, metrics, certifications, production AWS deployments, or repository URLs.
- A URL may be published in the README only when `url_verified: true` and the validator's `--check-links` run has seen it resolve.
- Floci is a local AWS-compatible emulator. k3s is not Amazon EKS. Say which tools are emulated APIs and which are real processes.
- Projects 01 and 02 stay at `implemented_learning_pending` until a learning reconstruction is recorded. Do not mark them `completed` because a repository already contains code. Project 01 is public; project 02 is not yet.
- Do not push, open pull requests, or change GitHub settings unless the maintainer asks in the current conversation.

## Check

From the repository root:

```bash
python3 scripts/validate_portfolio.py --check-links
```

The same command runs in `.github/workflows/validate-portfolio.yml`.
