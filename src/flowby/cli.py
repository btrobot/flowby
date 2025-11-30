#!/usr/bin/env python
"""
DSL Runner - Standalone Entry Point

Run DSL workflow scripts with various browser backends.

Usage:
    regflow --browser playwright test_pages/test_form.flow
    regflow --browser chromium --headless my_script.flow
"""

from .runner import main

if __name__ == "__main__":
    main()
