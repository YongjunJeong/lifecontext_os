#!/usr/bin/env python3
"""LifeContext OS 공개 저장소 품질 검사.

검사 범위:
- 공개 저장소에 추적되면 안 되는 로컬 파일
- 템플릿에 실수로 들어간 개인정보 패턴
- README가 참조하는 로컬 문서 링크
- 포트폴리오용 예시 파일 존재 여부
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_TRACKED = {
    ".DS_Store",
    ".env",
    ".env.local",
}

FORBIDDEN_PREFIXES = (
    ".venv/",
    "venv/",
    "env/",
    "__pycache__/",
    ".pytest_cache/",
    "private/",
    "personal/",
    "filled/",
    "vault.local/",
)

SENSITIVE_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "korean_phone": re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"),
    "korean_rrn": re.compile(r"\b\d{6}-?[1-4]\d{6}\b"),
}

ALLOWLIST_EMAILS = {
    "146877319+YongjunJeong@users.noreply.github.com",
}


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def check_forbidden_tracked(files: list[str], failures: list[str]) -> None:
    for path in files:
        name = Path(path).name
        if name in FORBIDDEN_TRACKED or path.startswith(FORBIDDEN_PREFIXES):
            fail(f"추적 금지 파일이 git에 포함됨: {path}", failures)


def check_sensitive_templates(failures: list[str]) -> None:
    targets = list((ROOT / "templates").glob("*.md"))
    targets += list((ROOT / "examples").glob("*.md"))
    for file_path in targets:
        text = file_path.read_text(encoding="utf-8")
        rel = file_path.relative_to(ROOT)
        for label, pattern in SENSITIVE_PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                if value in ALLOWLIST_EMAILS:
                    continue
                fail(f"{rel}에 민감정보 패턴 감지({label}): {value}", failures)


def check_readme_links(failures: list[str]) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    local_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    for link in local_links:
        if link.startswith(("http://", "https://", "#")):
            continue
        target = (ROOT / link).resolve()
        if not str(target).startswith(str(ROOT.resolve())):
            fail(f"README 로컬 링크가 저장소 밖을 가리킴: {link}", failures)
        elif not target.exists():
            fail(f"README 로컬 링크 대상 없음: {link}", failures)


def check_required_examples(failures: list[str]) -> None:
    required = [
        ROOT / "examples" / "decision_job_change.md",
    ]
    for path in required:
        if not path.exists():
            fail(f"필수 예시 파일 없음: {path.relative_to(ROOT)}", failures)


def main() -> int:
    failures: list[str] = []
    files = git_ls_files()

    check_forbidden_tracked(files, failures)
    check_sensitive_templates(failures)
    check_readme_links(failures)
    check_required_examples(failures)

    if failures:
        print("품질 검사 실패")
        for item in failures:
            print(f"- {item}")
        return 1

    print("품질 검사 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
