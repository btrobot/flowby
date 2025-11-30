# 🌸 Flowby

**Elegant Web Automation DSL**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/flowby/flowby?style=social)](https://github.com/flowby/flowby)

Flowby is a declarative, Python-style DSL for web automation and workflow orchestration. Write automation scripts that flow naturally.

---

## ✨ Features

- 🎯 **Declarative Syntax** - Describe *what* to do, not *how* to do it
- 🐍 **Python-Style** - Indentation-based blocks, familiar to Python developers
- 🌐 **Web Automation** - Browser control, element interaction, assertions
- 🔌 **OpenAPI Integration** - Auto-generate API clients from OpenAPI specs
- 📦 **Module System** - Reusable libraries with `import`/`export`
- ⚡ **Built-in Services** - HTTP client, random data generation, and more
- 🎭 **High-Level Abstraction** - Business-level operations, not DOM manipulation

---

## 🚀 Quick Start

### Installation

```bash
pip install flowby
```

### Hello World

```flow
# hello.flow
step "Greet the world":
    log "Hello, Flowby! 🌸"
```

Run it:
```bash
flowby hello.flow
```

### Web Automation Example

```flow
# login.flow
step "User Login":
    navigate to "https://example.com/login"

    type "user@example.com" into "#email"
    type "password123" into "#password"

    click "#submit"

    wait for navigation
    assert url contains "dashboard"
    log success "Login successful!"
```

### API Integration Example

```flow
# api_demo.flow
let user_api = Resource("openapi:specs/user-service.yml")

step "Fetch User Data":
    let user = user_api.getUser(userId=123)
    log "User: {user.name}, Email: {user.email}"

    assert user.status == "active"
```

---

## 📖 Documentation

- [Getting Started](docs/getting-started.md)
- [Language Reference](docs/language-reference.md)
- [Examples](examples/)
- [API Documentation](docs/api/)

---

## 🎯 Language Features

### Control Flow
```flow
# If-else
if status == 200:
    log "Success"
else:
    log "Failed"

# For loops with unpacking
for index, item in enumerate(items):
    log "{index}: {item.name}"

# While loops
while retry < 3:
    if check_status():
        break
    retry = retry + 1
```

### Functions
```flow
function validate_email(email):
    return email contains "@" and email contains "."

let is_valid = validate_email("user@example.com")
```

### Module System
```flow
# libs/utils.flow
library utils

export function log_phase(phase_name):
    log info "=== {phase_name} ==="

# main.flow
import utils from "libs/utils.flow"

utils.log_phase("Data Preparation")
```

### OpenAPI Resources
```flow
resource api:
    spec: "openapi/api.yml"
    auth: {type: "bearer", token: env.API_TOKEN}

    resilience:
        retry: {max_retries: 3, strategy: "exponential"}
        circuit_breaker: {failure_threshold: 5}

    mock:
        enabled: False
        responses: {getUser: {data: {id: 1}}}

let user = api.getUser(userId=123)
```

---

## 🏗️ Project Structure

```
flowby/
├── src/flowby/          # Core interpreter
│   ├── lexer.py         # Tokenization
│   ├── parser.py        # AST generation
│   ├── interpreter.py   # Execution engine
│   └── ...
├── tests/               # Test suite
├── examples/            # Example scripts
├── grammar/             # Language specification
└── docs/                # Documentation
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/flowby/flowby.git
cd flowby

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
flake8 src/
```

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Why Flowby?

| Feature | Playwright/Puppeteer | Flowby |
|---------|---------------------|--------|
| **Abstraction Level** | Low (DOM manipulation) | High (business operations) |
| **Syntax** | JavaScript/Python code | Declarative DSL |
| **OpenAPI Integration** | Manual implementation | Auto-generated clients |
| **Module System** | Language-dependent | Built-in library system |
| **Learning Curve** | Steep | Gentle |

**Flowby = Automation flows by design** 🌸

---

## 💬 Community

- [GitHub Discussions](https://github.com/flowby/flowby/discussions)
- [Discord Server](https://discord.gg/flowby)
- [Twitter](https://twitter.com/flowbylang)

---

## 🙏 Acknowledgments

Inspired by:
- Playwright (web automation)
- Ansible (declarative workflows)
- Python (elegant syntax)

---

<p align="center">
  Made with 🌸 by the Flowby team
</p>
