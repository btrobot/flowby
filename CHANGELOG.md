# Changelog

All notable changes to Flowby will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **VR-003 Duplicate Declaration Prevention** (v6.3) - Same-scope duplication check
  - Prevents redeclaration of variables/constants in same scope
  - Allows variable shadowing in nested scopes (functions, loops)
  - Detects parameter-local variable naming conflicts
  - Detects import-declaration conflicts
  - Simplified symbol registration logic
  - 22 comprehensive test cases
- **VR-002 Const Reassignment Checking** (v6.3) - Parser-stage const protection
  - Prevents modification of const-declared variables
  - Detects violations before runtime execution
  - Error messages include original definition line number
  - Suggests using 'let' for mutable variables
  - 8 dedicated test cases
- **VR-004 System Variable Readonly** (v6.3) - System variable protection
  - Prevents modification of system variables (page, env, response)
  - Checked before const validation (higher priority)
  - Clear error messages explaining readonly nature
  - 6 dedicated test cases + 11 combined tests
- **VR-001 Variable Undefined Checking** (v6.3) - Parser-stage variable validation
  - Detects undefined variables before runtime
  - Comprehensive error messages with VR-001 violation markers
  - System variables (page, env, response) exempted from checking
  - 25 comprehensive test cases covering all scenarios
- **Enhanced Symbol Table** (v6.3) - Extended symbol type support
  - `SymbolType.LOOP_VARIABLE` - For loop variables
  - `SymbolType.PARAMETER` - Function parameters
  - `SymbolType.MODULE` - Import module aliases
  - `SymbolType.IMPORTED` - Imported members
- **Improved Parser Scope Management** (v6.3) - Symbol registration during parsing
  - For loop variables registered before loop body
  - Function scope creation with parameter registration
  - Import symbols registered for VR-001 checking
  - Exception-safe scope management with try-finally blocks
- **Resource() constructor function** (v6.0) - Modern replacement for `resource` statement
  - Dynamic API client creation with `Resource(spec_file, **options)`
  - Full parameter support: base_url, auth, timeout, headers, resilience, mock
  - Automatic ExecutionContext injection
  - 17 comprehensive unit tests
- Initial public release of Flowby
- Python-style DSL for web automation (v3.0+)
- User-defined functions (v4.3)
- Module system with import/export (v5.0)
- Interactive input expression (v5.1)
- Browser automation with Playwright
- Built-in HTTP client and random data services
- Comprehensive test suite (1171+ tests)
- Complete grammar documentation
- Example scripts and tutorials

### Changed
- **Documentation Organization** (v6.3) - Structured technical analysis reports
  - Created `docs/analysis/` directory for technical analysis reports
  - Organized 5 comprehensive analysis reports:
    - Flowby_DSL_深度分析报告.md (~25,000 words) - Overall DSL analysis
    - Parser阶段语义检查详解.md (~20,000 words) - Semantic checking explanation
    - 编译器遗产价值分析.md (~15,000 words) - Compiler design legacy analysis
    - 语义检查系统完整分析报告.md (~30,000 words) - Semantic system analysis
    - type_语法设计分析.md (~12,000 words) - Type syntax design analysis
  - Added comprehensive README.md with reading guide
  - Removed obsolete introspection feature analysis reports
  - Total: ~102,000 words of technical documentation
- Migrated from v2.x block syntax to Python-style indentation (v3.0)
- Removed JavaScript-style API methods (`.length()`, `.toUpperCase()`)
- Updated all examples to v3.0+ syntax

### Removed
- **Violation Collection System** (v6.3) - Simplified to immediate ParserError mode
  - Removed `Violation` class from parser.py
  - Removed `violations` list tracking
  - Removed `get_violations()`, `get_violations_dict()` methods
  - VR rules now throw ParserError immediately instead of collecting violations
  - Rationale: Consistent error handling, simpler codebase
- **Dry-Run Feature** (v6.3) - Removed unimplemented feature
  - Removed `--dry-run` mode from runner
  - Removed `_print_dry_run_summary()` and related methods
  - Deleted `DRY_RUN_FEATURE.md` documentation
  - Rationale: Feature was incomplete and incompatible with ParserError mode
- **Introspection System** (v6.3) - Removed unused dead code
  - Removed `to_dict()` methods from ASTNode, Symbol, FunctionSymbol, SymbolTable, SymbolTableStack
  - Removed `_record_scope_change()` and `_record_assertion()` from Interpreter
  - Removed `get_ast()`, `get_ast_dict()`, `get_introspection_data()`, `get_symbol_table()`, `get_execution_history()` from DSLRunner
  - Removed `get_symbol_table()`, `get_symbol_table_dict()` from Parser
  - Removed introspection_callback parameter and related infrastructure
  - Total reduction: 354 lines of dead code (0% usage in 1171 tests)
  - Rationale: YAGNI principle - implemented but never used, simplified codebase
- **BREAKING**: `resource` statement syntax (v6.0) - Use `Resource()` function instead
  - Removed `resource <name> from <file>` syntax
  - Removed `resource <name>:` block syntax
  - Migration: `resource api from "spec.yml"` → `let api = Resource("spec.yml")`

### Fixed
- Module import errors in CLI
- Indentation validation (4-space multiples)
- Pytest marker warnings (361 → 0)
- Example scripts syntax compatibility

## [0.1.0] - 2025-11-30

### Added
- First tagged release
- Core DSL interpreter
- Lexer and Parser
- AST-based execution engine
- Browser automation support
- OpenAPI integration
- Module system
- User functions
- Full test coverage

---

## Version History

### Grammar Versions

- **v6.0** (2025-11-30) - Resource Constructor Function (BREAKING)
- **v5.1** (2025-11-30) - Input Expression
- **v5.0** (2025-11-30) - Module System
- **v4.3** (2025-11-29) - User-Defined Functions
- **v4.2** (2025-11-28) - OpenAPI Resources (deprecated in v6.0)
- **v4.0** (2025-11-27) - For Loop Multi-Variable
- **v3.2** (2025-11-26) - Action Statement Expressions
- **v3.1** (2025-11-25) - Service Call Syntax, When OR
- **v3.0** (2025-11-24) - Python-Style Indentation

---

For detailed grammar changes, see [grammar/CHANGELOG.md](grammar/CHANGELOG.md)
