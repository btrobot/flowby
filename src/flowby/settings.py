"""
Project-level settings and directory configuration

Defines the directory structure for Flowby project outputs.
"""

from pathlib import Path


class Settings:
    """
    Project settings for directory paths

    All paths are relative to the current working directory
    where the flowby command is executed.
    """

    # Base output directory
    OUTPUT_DIR = Path.cwd() / "flowby-output"

    # Screenshots directory (organized by date)
    # Structure: flowby-output/screenshots/YYYY-MM-DD/task-{id}-{time}/
    SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"

    # Logs directory (organized by date)
    # Structure: flowby-output/logs/YYYY-MM-DD/scriptname_HHMMSS_id.log
    LOGS_DIR = OUTPUT_DIR / "logs"

    # Diagnosis reports directory
    DIAGNOSIS_DIR = OUTPUT_DIR / "diagnosis"

    @classmethod
    def ensure_directories(cls):
        """
        Create all required directories if they don't exist

        Called automatically when ExecutionContext is initialized.
        """
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DIAGNOSIS_DIR.mkdir(parents=True, exist_ok=True)
