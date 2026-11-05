#!/usr/bin/env python3
"""Validate the bilingual portfolio index against projects/projects.yaml.

The YAML file is the source of truth. READMEs must repeat each project row
exactly enough for GitHub to show the same facts. Stack documents must not
mark a tool as seen in a private repository unless this script allows it.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "projects" / "projects.yaml"

REQUIRED_SLUGS = {
    "floci-cloud-foundation",
    "floci-event-driven-commerce",
    "floci-container-delivery",
    "floci-sre-observability",
    "floci-kubernetes-platform",
    "floci-multi-account-landing-zone",
    "floci-streaming-analytics",
    "floci-internal-developer-platform",
}

REQUIRED_HEADINGS = {
    "README.md": [
        "## Introduction",
        "## Learning philosophy",
        "## Project roadmap",
        "## Learning progression",
        "## Technology stack",
        "## Featured projects",
        "## Reproducibility",
        "## Disclaimer",
    ],
    "README.es.md": [
        "## Introducción",
        "## Filosofía de aprendizaje",
        "## Hoja de ruta",
        "## Progresión de aprendizaje",
        "## Stack tecnológico",
        "## Proyectos destacados",
        "## Reproducibilidad",
        "## Aviso",
    ],
    "docs/roadmap.en.md": [
        "## How the path is ordered",
        "## Sequence",
        "## Public repositories",
        "## Not started",
    ],
    "docs/roadmap.es.md": [
        "## Cómo está ordenado el camino",
        "## Secuencia",
        "## Repositorios públicos",
        "## Sin empezar",
    ],
    "docs/learning-methodology.en.md": [
        "## Order of work",
        "## What each step is for",
        "## Reconstruction",
        "## Evidence",
    ],
    "docs/learning-methodology.es.md": [
        "## Orden de trabajo",
        "## Para qué sirve cada paso",
        "## Reconstrucción",
        "## Evidencia",
    ],
    "docs/technology-stack.en.md": [
        "## How to read this list",
        "## Emulated APIs and real processes",
        "## Categories",
    ],
    "docs/technology-stack.es.md": [
        "## Cómo leer esta lista",
        "## APIs emuladas y procesos reales",
        "## Categorías",
    ],
    "projects/schema.en.md": [
        "## Source of truth",
        "## Fields",
        "## Status values",
        "## Difficulty values",
        "## Register a project",
        "## Update progress",
        "## Add a GitHub link",
        "## Featured projects",
        "## Keep both languages aligned",
        "## Validate",
    ],
    "projects/schema.es.md": [
        "## Fuente de verdad",
        "## Campos",
        "## Valores de estado",
        "## Valores de dificultad",
        "## Registrar un proyecto",
        "## Actualizar el progreso",
        "## Agregar un enlace de GitHub",
        "## Proyectos destacados",
        "## Mantener los dos idiomas alineados",
        "## Validar",
    ],
    "assets/diagrams/README.en.md": ["## Purpose"],
    "assets/diagrams/README.es.md": ["## Propósito"],
}

PAIRS = [
    ("README.md", "README.es.md"),
    ("docs/roadmap.en.md", "docs/roadmap.es.md"),
    ("docs/learning-methodology.en.md", "docs/learning-methodology.es.md"),
    ("docs/technology-stack.en.md", "docs/technology-stack.es.md"),
    ("projects/schema.en.md", "projects/schema.es.md"),
    ("assets/diagrams/README.en.md", "assets/diagrams/README.es.md"),
]

DIAGRAM_PAIRS = [
    ("README.md", "README.es.md"),
    ("docs/roadmap.en.md", "docs/roadmap.es.md"),
    ("docs/learning-methodology.en.md", "docs/learning-methodology.es.md"),
    ("docs/technology-stack.en.md", "docs/technology-stack.es.md"),
]

PUBLISHED_STATUS = {
    "en": "Named in a published lab",
    "es": "Nombrado en un laboratorio publicado",
}
PRIVATE_STATUS = {
    "en": "Seen in a private repository",
    "es": "Visto en un repositorio privado",
}
UNPUBLISHED_STATUS = {
    "en": "No lab published yet",
    "es": "Aún no hay laboratorio publicado",
}

# Tools present in the public project 01 repository.
NAMED_IN_PUBLISHED_LAB = {
    "Floci",
    "Floci UI",
    "AWS CLI",
    "Terraform",
    "Docker",
    "Docker Compose",
    "SQS",
    "S3",
    "DynamoDB",
}

# Tools present only in the retired private project 02 copy so far.
SEEN_IN_PRIVATE_REPOSITORY = {
    "AWS SDK",
    "Go",
    "Lambda",
    "API Gateway",
    "Step Functions",
    "EventBridge",
    "IAM",
}

# Curriculum tools with no lab evidence in this index yet.
# Remove a name only after a repository shows the tool,
# and move it into NAMED_IN_PUBLISHED_LAB or SEEN_IN_PRIVATE_REPOSITORY.
MUST_NOT_CLAIM = {
    "SNS",
    "ECS",
    "ECR",
    "ALB",
    "Jenkins",
    "CodeBuild",
    "CodePipeline",
    "CodeDeploy",
    "k3s",
    "Kubernetes",
    "Helm",
    "Kustomize",
    "Argo CD",
    "Forgejo",
    "RBAC",
    "IAM Pod Identity",
    "RDS",
    "Redis",
    "MSK",
    "Kinesis",
    "Firehose",
    "Glue",
    "Athena",
    "OpenSearch",
    "CloudWatch",
    "Prometheus",
    "Grafana",
    "Loki",
    "Grafana Alloy",
    "OpenTelemetry",
    "Jaeger",
    "Alertmanager",
    "k6",
    "Toxiproxy",
    "STS",
    "AWS Organizations",
    "SCP",
    "CloudTrail",
}

SKIP_CELLS = {
    "Tool",
    "Herramienta",
    "Status",
    "Estado",
    "Kind",
    "Tipo",
    "Meaning",
    "Significado",
    "Emulated API",
    "Real process",
    "Client",
    "API emulada",
    "Proceso real",
    "Cliente",
    PUBLISHED_STATUS["en"],
    PUBLISHED_STATUS["es"],
    PRIVATE_STATUS["en"],
    PRIVATE_STATUS["es"],
    UNPUBLISHED_STATUS["en"],
    UNPUBLISHED_STATUS["es"],
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
FENCE_RE = re.compile(r"^```", re.MULTILINE)
MERMAID_RE = re.compile(r"^```mermaid\s*$", re.MULTILINE)

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def headings(text: str) -> list[str]:
    found: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            found.append(line.strip())
    return found


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    in_fence = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""
    collected: list[str] = []
    in_fence = False
    for line in lines[start:]:
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected)


def tool_names(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if not parts:
            continue
        cell = parts[0]
        if not cell or cell.startswith("-") or cell in SKIP_CELLS:
            continue
        names.append(cell)
    return names


def documentation_belongs_to_project(project_url: str, slug: str, doc_url: str) -> bool:
    project_root = project_url.rstrip("/")
    if doc_url.startswith(project_root + "/"):
        return True
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)", project_root)
    if not match:
        return False
    owner, repo = match.group(1), match.group(2)
    if repo != slug:
        return False
    pages_root = f"https://{owner}.github.io/{repo}"
    return doc_url == pages_root or doc_url.startswith(pages_root + "/")


def check_tool_catalog(relative: str, language: str) -> None:
    text = read_text(relative)
    found = tool_names(text)
    expected = NAMED_IN_PUBLISHED_LAB | SEEN_IN_PRIVATE_REPOSITORY | MUST_NOT_CLAIM
    if set(found) != expected:
        missing = sorted(expected - set(found))
        extra = sorted(set(found) - expected)
        if missing:
            fail(f"{relative} is missing tool rows: {', '.join(missing)}")
        if extra:
            fail(f"{relative} has tool rows outside the validator lists: {', '.join(extra)}")
    published = PUBLISHED_STATUS[language]
    private = PRIVATE_STATUS[language]
    unpublished = UNPUBLISHED_STATUS[language]
    by_name = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cell = line.strip().strip("|").split("|")[0].strip()
        if cell in expected:
            by_name[cell] = line
    for name in sorted(NAMED_IN_PUBLISHED_LAB):
        line = by_name.get(name, "")
        if published not in line or private in line or unpublished in line:
            fail(f"{relative} must mark {name} as {published}")
    for name in sorted(SEEN_IN_PRIVATE_REPOSITORY):
        line = by_name.get(name, "")
        if private not in line or published in line or unpublished in line:
            fail(f"{relative} must mark {name} as {private}")
    for name in sorted(MUST_NOT_CLAIM):
        line = by_name.get(name, "")
        if unpublished not in line or published in line or private in line:
            fail(f"{relative} must mark {name} as {unpublished}")


def check_relative_links(relative: str, text: str) -> None:
    source = ROOT / relative
    for match in LINK_RE.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:")):
            if "localhost" in target or "127.0.0.1" in target:
                fail(f"{relative} links to a local address: {target}")
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (source.parent / path_part).resolve()
        if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
            fail(f"{relative} link escapes the repository: {target}")
            continue
        if not resolved.is_file():
            fail(f"{relative} broken relative link: {target}")


def check_secrets() -> None:
    needles = [
        "BEGIN " + "PRIVATE KEY",
        "BEGIN " + "OPENSSH PRIVATE KEY",
        "gh" + "p_",
        "github_" + "pat_",
        "/" + "Users/",
    ]
    access_key = re.compile(r"AKIA[0-9A-Z]{16}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".yml", ".yaml", ".py", ".txt"} and path.name != "LICENSE":
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for needle in needles:
            if needle in text:
                fail(f"{relative} contains forbidden material ({needle})")
        if access_key.search(text):
            fail(f"{relative} contains an AWS access key id pattern")


def localized(value: object, language: str, label: str) -> str:
    if not isinstance(value, dict):
        fail(f"{label} must be a mapping with en and es")
        return ""
    text = value.get(language, "")
    if not isinstance(text, str) or not text.strip():
        fail(f"{label}.{language} is empty")
        return ""
    return text


def validate_projects(data: dict) -> list[dict]:
    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    statuses = data.get("statuses")
    difficulties = data.get("difficulties")
    projects = data.get("projects")
    if not isinstance(statuses, dict) or not isinstance(difficulties, dict):
        fail("statuses and difficulties must be mappings")
        return []
    if not isinstance(projects, list):
        fail("projects must be a list")
        return []
    expected_status = {
        "planned",
        "in_progress",
        "implemented_learning_pending",
        "completed",
        "archived",
    }
    expected_difficulty = {"foundational", "intermediate", "advanced"}
    if set(statuses) != expected_status:
        fail(f"status keys must be {sorted(expected_status)}")
    if set(difficulties) != expected_difficulty:
        fail(f"difficulty keys must be {sorted(expected_difficulty)}")
    for key, labels in list(statuses.items()) + list(difficulties.items()):
        localized(labels, "en", key)
        localized(labels, "es", key)
    slugs: list[str] = []
    ids: list[str] = []
    for project in projects:
        if not isinstance(project, dict):
            fail("each project must be a mapping")
            continue
        project_id = str(project.get("id", ""))
        slug = str(project.get("slug", ""))
        if not re.fullmatch(r"\d{2}", project_id):
            fail(f"{slug or project_id}: id must be two digits")
        ids.append(project_id)
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            fail(f"{project_id}: slug must be lowercase")
        slugs.append(slug)
        name_en = localized(project.get("name"), "en", f"{slug}.name")
        name_es = localized(project.get("name"), "es", f"{slug}.name")
        description_en = localized(project.get("description"), "en", f"{slug}.description")
        description_es = localized(project.get("description"), "es", f"{slug}.description")
        if name_en and name_en == name_es:
            fail(f"{slug}: English and Spanish names must differ")
        if description_en and description_en == description_es:
            fail(f"{slug}: English and Spanish descriptions must differ")
        technologies = project.get("technologies")
        if not isinstance(technologies, list) or not technologies:
            fail(f"{slug}: technologies must be a non-empty list")
        elif any(not isinstance(item, str) or not item.strip() for item in technologies):
            fail(f"{slug}: technologies must be non-empty strings")
        if project.get("difficulty") not in difficulties:
            fail(f"{slug}: unknown difficulty")
        if project.get("status") not in statuses:
            fail(f"{slug}: unknown status")
        url = project.get("url")
        verified = project.get("url_verified")
        if not isinstance(verified, bool):
            fail(f"{slug}: url_verified must be a boolean")
        if verified:
            if not isinstance(url, str) or not url.startswith("https://github.com/"):
                fail(f"{slug}: a verified url must be an https GitHub URL")
            elif not url.rstrip("/").endswith("/" + slug):
                fail(f"{slug}: verified url must end with the slug")
        elif url is not None:
            fail(f"{slug}: unverified projects must set url to null")
        documentation = project.get("documentation")
        if not isinstance(documentation, list):
            fail(f"{slug}: documentation must be a list")
        else:
            for item in documentation:
                if not isinstance(item, dict):
                    fail(f"{slug}: documentation entries must be mappings")
                    continue
                localized(item.get("label"), "en", f"{slug}.documentation")
                localized(item.get("label"), "es", f"{slug}.documentation")
                doc_url = item.get("url")
                if not isinstance(doc_url, str) or not doc_url.startswith("https://"):
                    fail(f"{slug}: documentation url must be https")
                elif not isinstance(url, str) or not documentation_belongs_to_project(url, slug, doc_url):
                    fail(f"{slug}: documentation url must live under the project url or its GitHub Pages site")
        demo = project.get("demo")
        if demo is not None:
            if not isinstance(demo, str) or not demo.startswith("https://"):
                fail(f"{slug}: demo must be null or an https URL")
            elif "localhost" in demo or "127.0.0.1" in demo:
                fail(f"{slug}: demo must not be a local address")
        if not isinstance(project.get("featured"), bool):
            fail(f"{slug}: featured must be a boolean")
        note = project.get("repository_note")
        if note is not None:
            localized(note, "en", f"{slug}.repository_note")
            localized(note, "es", f"{slug}.repository_note")
    if len(ids) != len(set(ids)):
        fail("project ids must be unique")
    if ids != sorted(ids):
        fail("projects must be ordered by id")
    if len(slugs) != len(set(slugs)):
        fail("project slugs must be unique")
    missing = REQUIRED_SLUGS - set(slugs)
    if missing:
        fail("missing required projects: " + ", ".join(sorted(missing)))
    return [project for project in projects if isinstance(project, dict)]


def check_readme_row(text: str, project: dict, language: str, statuses: dict, difficulties: dict) -> None:
    project_id = project["id"]
    name = localized(project["name"], language, project["slug"])
    rows = [
        line
        for line in text.splitlines()
        if f"| {project_id} |" in line and name in line
    ]
    if len(rows) != 1:
        fail(f"README {language} must contain exactly one table row for {project_id}")
        return
    row = rows[0]
    slug = project["slug"]
    checks = [
        localized(project["name"], language, slug),
        localized(project["description"], language, slug),
        statuses[project["status"]][language],
        difficulties[project["difficulty"]][language],
        slug,
    ]
    technologies = project.get("technologies")
    if isinstance(technologies, list):
        checks.extend(technologies)
    for expected in checks:
        if expected and expected not in row:
            fail(f"README {language} row {project_id} is missing {expected!r}")
    url = project.get("url")
    if url:
        if url not in row:
            fail(f"README {language} row {project_id} is missing {url}")
    elif "https://" in row:
        fail(f"README {language} row {project_id} must not link an unpublished repository")


def check_unpublished_urls(texts: dict[str, str], projects: list[dict]) -> None:
    for project in projects:
        if project.get("url"):
            continue
        slug = project["slug"]
        pattern = re.compile(rf"https://github\.com/[^/\s)]+/{re.escape(slug)}(?:/|\b)")
        for relative, text in texts.items():
            if pattern.search(text):
                fail(f"{relative} links unpublished repository {slug}")


def check_featured(readme_en: str, readme_es: str, projects: list[dict]) -> None:
    featured = [project for project in projects if project.get("featured") is True]
    empty_en = "No project is featured yet."
    empty_es = "Ningún proyecto está destacado todavía."
    if not featured:
        if empty_en not in readme_en:
            fail("README.md must say that no project is featured yet")
        if empty_es not in readme_es:
            fail("README.es.md must say that no project is featured yet")
        return
    if empty_en in readme_en or empty_es in readme_es:
        fail("remove the empty featured sentence when a project is featured")
    english_section = section(readme_en, "## Featured projects")
    spanish_section = section(readme_es, "## Proyectos destacados")
    for project in featured:
        if project["name"]["en"] not in english_section:
            fail(f"featured section is missing {project['name']['en']}")
        if project["name"]["es"] not in spanish_section:
            fail(f"featured section is missing {project['name']['es']}")


def collect_https_links(texts: dict[str, str], projects: list[dict]) -> list[str]:
    found: set[str] = set()
    for text in texts.values():
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith("https://"):
                found.add(target)
    for project in projects:
        if isinstance(project.get("url"), str):
            found.add(project["url"])
        if isinstance(project.get("demo"), str):
            found.add(project["demo"])
        for item in project.get("documentation") or []:
            if isinstance(item, dict) and isinstance(item.get("url"), str):
                found.add(item["url"])
    return sorted(found)


def check_links(urls: list[str]) -> None:
    for url in urls:
        request = urllib.request.Request(url, headers={"User-Agent": "floci-portfolio-validator"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    fail(f"{url} returned HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            fail(f"{url} returned HTTP {exc.code}")
        except urllib.error.URLError as exc:
            fail(f"{url} could not be reached: {exc.reason}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the portfolio index")
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Request every https link and keep only HTTP 200",
    )
    args = parser.parse_args()

    if not YAML_PATH.is_file():
        print("missing projects/projects.yaml", file=sys.stderr)
        return 1
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("projects.yaml must be a mapping", file=sys.stderr)
        return 1

    projects = validate_projects(data)
    texts = {relative: read_text(relative) for relative in REQUIRED_HEADINGS}
    for relative, text in texts.items():
        if len(text) < 400:
            fail(f"{relative} is too short to be a real document")
        for heading in REQUIRED_HEADINGS[relative]:
            if heading not in headings(text):
                fail(f"{relative} is missing heading {heading}")
        if FENCE_RE.findall(text).__len__() % 2 != 0:
            fail(f"{relative} has an unbalanced code fence")
        check_relative_links(relative, text)

    for english, spanish in PAIRS:
        english_name = Path(english).name
        spanish_name = Path(spanish).name
        if spanish_name not in "\n".join(texts[english].splitlines()[:5]):
            fail(f"{english} must link to {spanish_name} near the top")
        if english_name not in "\n".join(texts[spanish].splitlines()[:5]):
            fail(f"{spanish} must link to {english_name} near the top")

    for english, spanish in DIAGRAM_PAIRS:
        english_count = len(MERMAID_RE.findall(texts[english]))
        spanish_count = len(MERMAID_RE.findall(texts[spanish]))
        if english_count != spanish_count or english_count < 1:
            fail(f"{english} and {spanish} must contain the same non-empty Mermaid set")

    readme_en = texts["README.md"]
    readme_es = texts["README.es.md"]
    if projects and isinstance(data.get("statuses"), dict) and isinstance(data.get("difficulties"), dict):
        for project in projects:
            check_readme_row(readme_en, project, "en", data["statuses"], data["difficulties"])
            check_readme_row(readme_es, project, "es", data["statuses"], data["difficulties"])
            note = project.get("repository_note")
            if isinstance(note, dict):
                if note.get("en") not in readme_en:
                    fail(f"README.md is missing the repository note for {project['slug']}")
                if note.get("es") not in readme_es:
                    fail(f"README.es.md is missing the repository note for {project['slug']}")
            for item in project.get("documentation") or []:
                if isinstance(item, dict) and item.get("url") not in readme_en:
                    fail(f"README.md is missing documentation URL {item.get('url')}")
                if isinstance(item, dict) and item.get("url") not in readme_es:
                    fail(f"README.es.md is missing documentation URL {item.get('url')}")
        check_featured(readme_en, readme_es, projects)
        check_unpublished_urls(texts, projects)

    check_tool_catalog("docs/technology-stack.en.md", "en")
    check_tool_catalog("docs/technology-stack.es.md", "es")
    check_secrets()

    if args.check_links and not ERRORS:
        check_links(collect_https_links(texts, projects))

    if ERRORS:
        print(f"{len(ERRORS)} portfolio check(s) failed:", file=sys.stderr)
        for message in ERRORS:
            print(f"- {message}", file=sys.stderr)
        return 1
    print("portfolio validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
