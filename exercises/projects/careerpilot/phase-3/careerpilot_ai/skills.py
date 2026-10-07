"""The skill vocabulary the match score uses (given — you may extend it, but the tests use exactly this list).

Matching rules the tests expect:
  - case-insensitive
  - whole words only: "sql" must NOT match inside "PostgreSQL" or "NoSQL", "git" must NOT match "GitHub"
  - multi-word skills ("github actions") match as a phrase
"""

SKILLS: tuple[str, ...] = (
    "python",
    "flask",
    "fastapi",
    "django",
    "sql",
    "postgresql",
    "docker",
    "kubernetes",
    "aws",
    "terraform",
    "git",
    "github actions",
    "react",
    "typescript",
    "javascript",
    "redis",
    "pytest",
    "graphql",
    "linux",
)
