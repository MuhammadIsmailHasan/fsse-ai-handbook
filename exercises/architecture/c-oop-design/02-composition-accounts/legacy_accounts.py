"""The 'before' version — read it, don't edit it. Count the classes you'd need for every role × plan combination."""


class User:
    def __init__(self, email):
        self.email = email

    def can(self, permission):
        return False


class JobSeeker(User):
    def can(self, permission):
        return permission in {"applications:read", "applications:write", "jobs:read"}


class Recruiter(User):
    def can(self, permission):
        return permission in {"jobs:read", "jobs:write", "candidates:read"}


class ProJobSeeker(JobSeeker):
    applications_limit = 1000

    def has_feature(self, feature):
        return feature in {"tracker", "ai_match", "export"}


class ProRecruiter(Recruiter):
    def has_feature(self, feature):
        return feature in {"tracker", "ai_match", "export"}


class RecruiterWhoIsAlsoJobSeeker(Recruiter, JobSeeker):  # 😬 multiple inheritance: which can() wins?
    pass


# Upgrading Siti to Pro means creating a new ProJobSeeker object and copying every field over.
