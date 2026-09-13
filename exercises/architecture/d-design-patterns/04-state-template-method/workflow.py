"""State and Template Method. See README.md."""

from abc import ABC, abstractmethod


class InvalidAction(Exception):
    pass


# TODO: state classes + ApplicationWorkflow
# TODO: ApplicationReport, PlainTextReport, MarkdownReport
