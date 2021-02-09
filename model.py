from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from dateutil import parser


@dataclass
class Environment:
    name: str
    created_at: str


@dataclass
class Status:
    name: str
    status: bool
    toggled_at: datetime = field(default=None)

    def __post_init__(self):
        if isinstance(self.toggled_at, str):
            self.toggled_at = parser.isoparse(self.toggled_at)


@dataclass
class Feature:
    name: str
    created_at: datetime
    status: dict
    feature_status: List[Status]

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = parser.isoparse(self.created_at)
        self.feature_status = [Status(**obj) for obj in self.feature_status]
