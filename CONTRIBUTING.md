# How to Contribute

We welcome contributions to the AISIP protocol.

## Ways to Contribute

- **Specification** — Propose changes to the protocol spec via issues or PRs
- **Reference Implementations** — Add implementations in new languages (Go, JS, Java, etc.)
- **Documentation** — Improve docs, add tutorials, fix typos
- **Test Cases** — Add test scenarios for edge cases

## Contribution Process

1. **Fork** the repository
2. **Create a feature branch** from `main`
3. **Make your changes** and ensure all tests pass
4. **Submit a pull request** with a clear description of the change

## Guidelines

- Keep the protocol simple — complexity is a bug, not a feature
- Reference implementations should have zero external dependencies
- All control flow patterns must have corresponding test cases
- Protocol changes require updating both the spec and reference implementation

## Running Tests

```bash
cd reference/python
python test_all.py
```

All tests must pass before submitting.

## Code of Conduct

Be respectful, constructive, and focused on making the protocol better for everyone.
