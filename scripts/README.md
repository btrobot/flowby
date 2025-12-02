# 提交前检查脚本使用说明

## 概述

为了避免 CI 失败，项目提供了本地检查脚本，在提交前验证代码质量。

## 脚本说明

### 1. 快速检查（推荐日常使用）

**用途**：只检查代码格式，速度快
**适用**：日常提交、快速验证

```bash
# Python 方式
python scripts/quick_check.py

# Windows 批处理（双击运行）
scripts\check.bat
```

**检查项目**：
- ✅ Black 代码格式化
- ✅ Flake8 代码风格检查

**耗时**：约 3-5 秒

---

### 2. 完整检查（提交重要代码时使用）

**用途**：完整的代码质量检查
**适用**：重要提交、发布前验证

```bash
# 完整检查（包含测试）
python scripts/pre_commit.py

# 跳过测试（性能受限时）
python scripts/pre_commit.py --skip-tests
```

**检查项目**：
- ✅ Black 代码格式化
- ✅ Flake8 代码风格检查
- ✅ MyPy 类型检查（可选）
- ✅ 单元测试（可选）

**耗时**：
- 跳过测试：约 10-15 秒
- 完整检查：约 30-60 秒（取决于设备性能）

---

## 使用建议

### 日常开发流程

```bash
# 1. 编写代码
# ...

# 2. 自动格式化
black src/ tests/

# 3. 快速检查
python scripts/quick_check.py

# 4. 如果通过，提交
git add .
git commit -m "feat: add new feature"
git push
```

### 重要提交流程

```bash
# 1. 完整检查（跳过测试）
python scripts/pre_commit.py --skip-tests

# 2. 如果通过，提交
git add .
git commit -m "release: v1.0.0"

# 3. 推送前运行完整测试（可选）
pytest tests/

# 4. 推送
git push
```

---

## 常见问题

### Q: 为什么不自动运行测试？

**A:** 根据性能考虑：
- 本地设备性能有限，完整测试可能需要 1-2 分钟
- GitHub CI 服务器性能更好，会自动运行完整测试
- 建议本地只检查格式和风格，让 CI 运行测试

### Q: Black 格式化失败怎么办？

**A:** 运行自动格式化：
```bash
black src/ tests/
```

### Q: Flake8 错误怎么修复？

**A:** 查看具体错误提示并手动修复：
```bash
# 查看详细错误
flake8 src/ tests/ --show-source
```

### Q: 可以跳过某些检查吗？

**A:** 可以：
- 快速检查：只运行 Black + Flake8
- `--skip-tests`：跳过 MyPy 和 pytest
- 手动运行单项检查：
  ```bash
  black --check src/
  flake8 src/
  mypy src/
  pytest tests/
  ```

---

## 工具配置

所有工具配置在 `pyproject.toml` 中：

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']

[tool.mypy]
python_version = "3.8"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## 与 Git Hook 集成（可选）

如果想要自动运行检查，可以设置 Git Hook：

### Windows (PowerShell)

```powershell
# 创建 pre-commit hook
@"
#!/bin/sh
python scripts/quick_check.py
"@ | Out-File -Encoding ASCII .git/hooks/pre-commit

# 添加执行权限（Git Bash）
chmod +x .git/hooks/pre-commit
```

### 禁用 Hook（临时）

```bash
git commit --no-verify -m "message"
```

---

## 性能对比

| 检查方式 | 本地设备 | GitHub CI |
|---------|---------|-----------|
| Black + Flake8 | ~5 秒 | ~3 秒 |
| 完整检查（跳过测试） | ~15 秒 | ~10 秒 |
| 完整检查（含测试） | ~60 秒 | ~30 秒 |

**建议**：
- 日常提交：只运行 Black + Flake8
- 重要提交：运行完整检查（跳过测试）
- 让 CI 运行完整测试套件

---

## 脚本维护

脚本位置：
- `scripts/quick_check.py` - 快速检查
- `scripts/pre_commit.py` - 完整检查
- `scripts/check.bat` - Windows 批处理快捷方式

修改检查项目请编辑对应的 Python 脚本。
