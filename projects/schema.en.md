**English** · [Español](schema.es.md)

# Project metadata

[Portfolio](../README.md)

`projects/projects.yaml` is the source of truth for project metadata. The English and Spanish READMEs repeat it so GitHub renders a readable index. A future site should read the YAML. The preferred shape for that site is a static Astro site. This repository does not contain that site.

## Source of truth

Change the YAML first, then both READMEs, then the stack tables if a tool moved between "seen in a private repository" and "no lab published yet". Run the validator before considering the change done.

```bash
python3 scripts/validate_portfolio.py
python3 scripts/validate_portfolio.py --check-links
```

`--check-links` requests every verified GitHub URL. Use it when a URL was added or changed. The structural command is enough for a wording change that does not touch URLs.

## Fields

| Field | Required | Rule |
| --- | --- | --- |
| `id` | Yes | Two digits, unique, used as the table key. Example: `"01"`. |
| `slug` | Yes | Repository name only, such as `floci-cloud-foundation`. Unique. |
| `name.en`, `name.es` | Yes | Display names. They must differ. |
| `description.en`, `description.es` | Yes | One sentence for the roadmap table. They must differ. The README row must contain this sentence exactly. |
| `technologies` | Yes | Learning-scope names. The roadmap row must list them. A published lab may implement only part of the list. |
| `difficulty` | Yes | `foundational`, `intermediate`, or `advanced`. A sequencing label, not a score. |
| `status` | Yes | One of the status keys below. |
| `url` | Yes, nullable | `https://github.com/<owner>/<slug>` or `null`. |
| `url_verified` | Yes | `true` only after the URL has been opened and it resolves. If `false`, `url` must be `null`. |
| `documentation` | Yes | List of `{label.en, label.es, url}`. Empty when nothing has been checked. Each URL must sit under the project URL. |
| `demo` | Yes, nullable | Public demo URL, or `null`. Do not put a localhost URL here. |
| `featured` | Yes | `true` only with implementation evidence and a conscious decision to feature it. |
| `repository_note` | No | `{en, es}` or `null`. Both READMEs must contain the text exactly. Use it for scope the table cannot say, such as a tool that is listed but not in the published Terraform. |

`schema_version` is `1`. Status and difficulty labels live next to their keys so a renderer does not invent translations.

## Status values

| Key | English | Español |
| --- | --- | --- |
| `planned` | Planned | Planificado |
| `in_progress` | In progress | En progreso |
| `implemented_learning_pending` | Implemented — learning/reconstruction pending | Implementado — reconstrucción y validación del aprendizaje pendientes |
| `completed` | Completed | Completado |
| `archived` | Archived | Archivado |

Use `implemented_learning_pending` when a repository contains implementation and the manual reconstruction from the [learning methodology](../docs/learning-methodology.en.md) is not recorded as done. Projects 01 and 02 are in that state. Do not use `completed` to mean "the repository exists".

## Difficulty values

| Key | English | Español |
| --- | --- | --- |
| `foundational` | Foundational | Fundacional |
| `intermediate` | Intermediate | Intermedio |
| `advanced` | Advanced | Avanzado |

## Register a project

1. Add an object under `projects` in `projects/projects.yaml` with both languages filled in.
2. Set `status: planned`, `url: null`, `url_verified: false`, `featured: false`, and `documentation: []` until there is evidence.
3. Add one roadmap row to `README.md` and the equivalent row to `README.es.md`. The row must contain the id, both the name and the description for that language, the difficulty label, the status label, and the slug.
4. If the project introduces a tool, add a row to both technology-stack files. A tool with no published evidence uses `No lab published yet` and stays in `MUST_NOT_CLAIM` inside `scripts/validate_portfolio.py`.
5. Add the same scope to [roadmap.en.md](../docs/roadmap.en.md) and [roadmap.es.md](../docs/roadmap.es.md).
6. Run the validator.

Do not create the application inside this repository. The lab gets its own repository.

## Update progress

Change `status` in the YAML, then replace the status cell in both README rows. Allowed moves:

| From | To | Evidence required |
| --- | --- | --- |
| `planned` | `in_progress` | A repository exists and work has started. Record the verified URL in the same change. |
| `in_progress` or `planned` | `implemented_learning_pending` | The repository contains the implementation. Say what is present in `repository_note`. Do not claim the manual path is done. |
| `implemented_learning_pending` | `completed` | The project repository records the manual reconstruction, and this index links that record. |
| any | `archived` | The project leaves the active path. Say why in `repository_note`. |

Do not invent a percentage, a test count, or a date of completion. If the only evidence is "a previous session said it passed", keep the more conservative status.

## Add a GitHub link

1. Confirm the repository exists and is the one you mean. Open the URL. `gh repo view <owner>/<slug>` is enough.
2. Set `url` to `https://github.com/<owner>/<slug>` and `url_verified: true`.
3. Add documentation links only for files you have opened. Each one needs an English label and a Spanish label.
4. Put the URL on the README row in both languages. Unpublished rows stay as inline code plus "Not published" or "No publicado", with no `https://` link.
5. Run `python3 scripts/validate_portfolio.py --check-links`.

A slug written in backticks is not a link. Do not guess the owner or the default branch.

## Featured projects

Set `featured: true` only when the implementation is complete enough to show in an interview and the note says what the reader will find. Then replace the sentence "No project is featured yet." in `README.md` and "Ningún proyecto está destacado todavía." in `README.es.md` with a short entry for each featured project. The validator rejects a featured flag that the README does not mention, and it rejects the empty-state sentence once any project is featured.

Projects 01 and 02 stay unfeatured while reconstruction is pending.

## Keep both languages aligned

English and Spanish documents carry the same structure, the same projects, and the same claims. Product names stay in English. Translations of status and difficulty labels come from the YAML, not from a paraphrase in the table.

When a sentence in `repository_note` changes, paste the new sentence into both READMEs. The validator compares them as exact text.

Files that must stay in pairs:

| English | Español |
| --- | --- |
| `README.md` | `README.es.md` |
| `docs/roadmap.en.md` | `docs/roadmap.es.md` |
| `docs/learning-methodology.en.md` | `docs/learning-methodology.es.md` |
| `docs/technology-stack.en.md` | `docs/technology-stack.es.md` |
| `projects/schema.en.md` | `projects/schema.es.md` |

## Validate

The validator checks the schema, exact README rows, featured copy, relative links, the absence of home-directory paths and obvious secret material, and the published-lab column in both stack documents.

`SEEN_IN_PRIVATE_REPOSITORY` and `MUST_NOT_CLAIM` in `scripts/validate_portfolio.py` are the lock on that column. Move a tool from one list to the other only after a repository shows it. Update both stack documents in the same change. The sentence in `PUBLISHED_STATUS` currently means the tool was seen in a retired private repository. Projects 01 and 02 will be rebuilt, and their portfolio slugs are not published. When a public repository exists, change that sentence in the validator and in both stack documents, and set `url_verified: true`.

The GitHub Actions workflow `.github/workflows/validate-portfolio.yml` runs the same command with `--check-links` on push and pull request. It does not deploy a site.
