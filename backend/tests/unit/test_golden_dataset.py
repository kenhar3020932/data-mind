"""Unit tests for golden dataset generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.golden.generate import GoldenDatasetGenerator


class TestGoldenDatasetGenerator:
    """Test suite for golden dataset generation."""

    def setup_method(self) -> None:
        self.generator = GoldenDatasetGenerator(seed=42)

    def test_generate_duplicate_dataset(self) -> None:
        """Test duplicate dataset generation."""
        dataset = self.generator.generate_duplicate_dataset(row_count=100, duplicate_rate=0.1)

        assert dataset["name"] == "duplicates"
        assert len(dataset["data"]) == 110  # 100 + 10 duplicates
        assert "manifest" in dataset
        assert dataset["manifest"]["planted_truths"]["exact_duplicates"] == 10

    def test_generate_outlier_dataset(self) -> None:
        """Test outlier dataset generation."""
        dataset = self.generator.generate_outlier_dataset(row_count=100, outlier_rate=0.05)

        assert dataset["name"] == "outliers"
        assert len(dataset["data"]) == 100
        assert dataset["manifest"]["planted_truths"]["outlier_count"] == 5

    def test_generate_missing_dataset(self) -> None:
        """Test missing value dataset generation."""
        dataset = self.generator.generate_missing_pattern_dataset(row_count=100, missing_rate=0.1)

        assert dataset["name"] == "missing_mcar"
        assert len(dataset["data"]) == 100
        assert dataset["manifest"]["planted_truths"]["pattern"] == "MCAR"

    def test_generate_all_datasets(self, tmp_path: Path) -> None:
        """Test generating all datasets to temp directory."""
        self.generator.generate_all_datasets(str(tmp_path))

        # Check that directories were created
        assert (tmp_path / "duplicates").exists()
        assert (tmp_path / "outliers").exists()
        assert (tmp_path / "missing_mcar").exists()

        # Check manifest files
        manifest = json.loads((tmp_path / "duplicates" / "manifest.json").read_text())
        assert "seed" in manifest
        assert "planted_truths" in manifest

    def test_reproducibility(self) -> None:
        """Test that same seed produces same data."""
        gen1 = GoldenDatasetGenerator(seed=123)
        gen2 = GoldenDatasetGenerator(seed=123)

        dataset1 = gen1.generate_duplicate_dataset(row_count=10)
        dataset2 = gen2.generate_duplicate_dataset(row_count=10)

        assert dataset1["data"] == dataset2["data"]