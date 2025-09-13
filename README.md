# dev-qol-toolkit

Quality-of-life utilities for Python engineers: JSON, files, logging, CLI, HTTP.
- Python 3.10+ (3.13 tested)
- Pure Python, typed
- Works as library **and** powers editor commands (VS Code / JetBrains plugins)

## Install
```bash
pip install dev-qol-toolkit

## Quickstart
```python
from dev_qol_toolkit import json_utils, file_utils, log_utils

data = json_utils.load_json("config.json")
flat = json_utils.flatten_json(data)

for p in file_utils.find_file("settings.py", "."):
    print(p)

logger = log_utils.setup_logging("INFO")
logger.info("Ready.")
```

## CLI
```bash
python3 -m dev_qol_toolkit.cli --help
```

---

## LICENSE (MIT)
```text
MIT License

Copyright (c) 2025 ...

Permission is hereby granted, free of charge, to any person obtaining a copy...