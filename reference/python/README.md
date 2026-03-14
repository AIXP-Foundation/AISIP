# AISIP Python Reference Implementation

Zero-dependency Python utilities for loading, validating, and running AISIP flow files.

## Files

| File | Purpose |
|------|---------|
| `flow_runtime.py` | Core library — loader, validator, flow analyzer, prompt builder |
| `run.py` | CLI tool — inspect and run `.aisip.json` files |
| `test_all.py` | Test suite — 16 tests covering all node types and flow patterns |
| `example.aisip.json` | Example flow file — greeting assistant |

## Quick Start

```bash
# Inspect a flow file
python run.py example.aisip.json

# Build a prompt (simulate runtime input)
python run.py example.aisip.json --prompt "I have a billing issue"

# Run all tests
python test_all.py
```

## API (flow_runtime.py)

```python
from flow_runtime import load, validate, render_flow, build_prompt

program = load("example.aisip.json")   # Load and parse
validate(program)                       # Structural validation (raises ValueError on error)
print(render_flow(program))             # Print ASCII flow diagram
prompt = build_prompt(program, user_input="hello")  # Build runtime prompt
```

## Requirements

- Python 3.10+
- Zero external dependencies (stdlib only)
