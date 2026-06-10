#!/usr/bin/env python3
from __future__ import annotations

from _bootstrap import read_event, write_event
from contextguard.context_capsule import persist_session_capsule
from contextguard.project import detect_project


event = read_event()
info = detect_project()
persist_session_capsule(info.root, event)
write_event({})
