"""Factory, Builder and a safe Singleton. See README.md."""

import json
import os
from dataclasses import dataclass
from functools import cache

EXPORTERS: dict[str, type] = {}

# TODO: register_exporter, create_exporter, CsvLinesExporter, JsonLinesExporter
# TODO: JobPosting, JobPostingBuilder
# TODO: Settings, load_settings, get_settings
