"""Golden dataset generator for DataMind-King validation tests.

Creates deterministic datasets with known properties for statistical
validation and benchmarking.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class GoldenDatasetGenerator:
    """Generates golden datasets with planted truths for validation."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_sales_dataset(self, num_rows: int = 10000) -> dict[str, Any]:
        """Generate sales dataset with known statistical properties.

        Args:
            num_rows: Number of rows to generate.

        Returns:
            Dictionary with dataset and expected metrics.
        """
        regions = ["North", "South", "East", "West"]
        products = ["Widget A", "Widget B", "Widget C", "Widget D"]
        customers = [f"CUST-{i:05d}" for i in range(1, 5001)]

        rows = []
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        total_revenue = 0.0
        total_orders = 0
        region_revenue: dict[str, float] = {r: 0.0 for r in regions}

        for i in range(num_rows):
            date = start_date + timedelta(days=self.rng.randint(0, 364))
            region = self.rng.choice(regions)
            product = self.rng.choice(products)
            customer = self.rng.choice(customers)
            quantity = self.rng.randint(1, 10)
            unit_price = self.rng.uniform(10.0, 500.0)
            revenue = quantity * unit_price

            row = {
                "order_id": f"ORD-{i+1:06d}",
                "date": date.strftime("%Y-%m-%d"),
                "region": region,
                "product": product,
                "customer_id": customer,
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
                "revenue": round(revenue, 2),
                "discount": round(self.rng.uniform(0, 0.2), 2),
            }
            rows.append(row)
            total_revenue += revenue
            total_orders += 1
            region_revenue[region] += revenue

        # Calculate expected metrics
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        unique_customers = len(set(r["customer_id"] for r in rows))
        top_region = max(region_revenue, key=region_revenue.get)

        return {
            "name": "Sales Analysis 2024",
            "description": "Annual sales transactions with known metrics",
            "row_count": num_rows,
            "columns": [
                "order_id",
                "date",
                "region",
                "product",
                "customer_id",
                "quantity",
                "unit_price",
                "revenue",
                "discount",
            ],
            "data": rows,
            "known_answers": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "unique_customers": unique_customers,
                "avg_order_value": round(avg_order_value, 2),
                "top_region": top_region,
                "region_revenue": {k: round(v, 2) for k, v in region_revenue.items()},
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31",
                },
            },
            "validation_queries": [
                {
                    "name": "total_revenue",
                    "sql": "SELECT SUM(revenue) FROM sales",
                    "expected": round(total_revenue, 2),
                },
                {
                    "name": "total_orders",
                    "sql": "SELECT COUNT(*) FROM sales",
                    "expected": total_orders,
                },
                {
                    "name": "unique_customers",
                    "sql": "SELECT COUNT(DISTINCT customer_id) FROM sales",
                    "expected": unique_customers,
                },
                {
                    "name": "avg_order_value",
                    "sql": "SELECT AVG(revenue) FROM sales",
                    "expected": round(avg_order_value, 2),
                },
                {
                    "name": "top_region",
                    "sql": (
                        "SELECT region FROM sales "
                        "GROUP BY region ORDER BY SUM(revenue) DESC LIMIT 1"
                    ),
                    "expected": top_region,
                },
            ],
        }

    def generate_customer_churn_dataset(self, num_rows: int = 5000) -> dict[str, Any]:
        """Generate customer churn dataset with known properties.

        Args:
            num_rows: Number of customer records.

        Returns:
            Dictionary with dataset and expected metrics.
        """
        rows = []
        churned_count = 0

        for i in range(num_rows):
            tenure = self.rng.randint(1, 72)  # months
            monthly_charges = self.rng.uniform(20.0, 100.0)
            total_charges = tenure * monthly_charges * self.rng.uniform(0.9, 1.1)
            contract_type = self.rng.choice(["Month-to-month", "One year", "Two year"])
            internet_service = self.rng.choice(["DSL", "Fiber optic", "No"])
            churn = self.rng.random() < 0.152  # 15.2% churn rate

            if churn:
                churned_count += 1

            row = {
                "customer_id": f"CUST-{i+1:05d}",
                "tenure": tenure,
                "monthly_charges": round(monthly_charges, 2),
                "total_charges": round(total_charges, 2),
                "contract_type": contract_type,
                "internet_service": internet_service,
                "churn": churn,
            }
            rows.append(row)

        churn_rate = churned_count / num_rows if num_rows > 0 else 0

        return {
            "name": "Customer Churn Prediction",
            "description": "Telecom customer churn dataset",
            "row_count": num_rows,
            "columns": [
                "customer_id",
                "tenure",
                "monthly_charges",
                "total_charges",
                "contract_type",
                "internet_service",
                "churn",
            ],
            "data": rows,
            "known_answers": {
                "churn_rate": round(churn_rate, 3),
                "churned_customers": churned_count,
                "retained_customers": num_rows - churned_count,
                "avg_tenure": round(sum(r["tenure"] for r in rows) / num_rows, 2),
                "avg_monthly_charges": round(
                    sum(r["monthly_charges"] for r in rows) / num_rows, 2
                ),
            },
            "validation_queries": [
                {
                    "name": "churn_rate",
                    "sql": "SELECT AVG(CAST(churn AS INTEGER)) FROM churn_data",
                    "expected": round(churn_rate, 3),
                },
                {
                    "name": "churned_customers",
                    "sql": "SELECT COUNT(*) FROM churn_data WHERE churn = true",
                    "expected": churned_count,
                },
            ],
        }

    def generate_anomaly_dataset(self, num_rows: int = 1000) -> dict[str, Any]:
        """Generate dataset with planted anomalies for detection testing.

        Args:
            num_rows: Number of rows to generate.

        Returns:
            Dictionary with dataset and anomaly information.
        """
        rows = []
        anomalies = []

        for i in range(num_rows):
            value = self.rng.gauss(100, 15)  # Normal distribution
            is_anomaly = False

            # Plant 5% anomalies
            if self.rng.random() < 0.05:
                value = self.rng.choice([
                    value + self.rng.uniform(50, 100),  # High anomaly
                    value - self.rng.uniform(50, 100),  # Low anomaly
                ])
                is_anomaly = True
                anomalies.append({
                    "row_index": i,
                    "value": round(value, 2),
                    "type": "statistical_outlier",
                })

            rows.append({
                "id": i,
                "timestamp": f"2024-10-0{i % 9 + 1}T{(i % 24):02d}:00:00Z",
                "value": round(value, 2),
                "is_anomaly": is_anomaly,
            })

        return {
            "name": "Anomaly Detection Test",
            "description": "Dataset with planted anomalies for detection validation",
            "row_count": num_rows,
            "columns": ["id", "timestamp", "value", "is_anomaly"],
            "data": rows,
            "known_answers": {
                "anomaly_count": len(anomalies),
                "anomaly_rate": round(len(anomalies) / num_rows, 3),
                "anomalies": anomalies[:10],  # First 10 for verification
            },
            "validation_queries": [
                {
                    "name": "anomaly_count",
                    "sql": "SELECT COUNT(*) FROM anomaly_data WHERE is_anomaly = true",
                    "expected": len(anomalies),
                },
            ],
        }

    def generate_duplicate_dataset(self, row_count: int = 1000, duplicate_rate: float = 0.1) -> dict[str, Any]:
        """Generate dataset with planted duplicates for detection testing.

        Args:
            num_rows: Base number of rows.
            duplicate_rate: Fraction of rows to duplicate.

        Returns:
            Dictionary with dataset and duplicate information.
        """
        base_rows = []
        for i in range(row_count):
            base_rows.append({
                "id": i,
                "value": self.rng.gauss(100, 15),
                "category": self.rng.choice(["A", "B", "C"]),
                "timestamp": f"2024-10-{(i % 28) + 1:02d}T{(i % 24):02d}:00:00Z",
            })

        # Generate duplicates
        num_duplicates = int(row_count * duplicate_rate)
        duplicates = []
        for _ in range(num_duplicates):
            source_idx = self.rng.randint(0, len(base_rows) - 1)
            duplicates.append(base_rows[source_idx].copy())

        all_rows = base_rows + duplicates
        self.rng.shuffle(all_rows)

        return {
            "name": "duplicates",
            "description": "Dataset with planted exact duplicates",
            "row_count": len(all_rows),
            "base_rows": row_count,
            "duplicate_count": num_duplicates,
            "columns": ["id", "value", "category", "timestamp"],
            "data": all_rows,
            "manifest": {
                "seed": self.seed,
                "planted_truths": {
                    "exact_duplicates": num_duplicates,
                    "base_unique": row_count,
                    "total_rows": len(all_rows),
                },
            },
        }

    def generate_outlier_dataset(self, row_count: int = 1000, outlier_rate: float = 0.05) -> dict[str, Any]:
        """Generate dataset with planted outliers for detection testing.

        Args:
            num_rows: Number of rows.
            outlier_rate: Fraction of outliers.

        Returns:
            Dictionary with dataset and outlier information.
        """
        rows = []
        num_outliers = int(row_count * outlier_rate)
        outlier_indices = set(self.rng.sample(range(row_count), num_outliers))

        for i in range(row_count):
            is_outlier = i in outlier_indices
            value = self.rng.gauss(100, 15)

            if is_outlier:
                value = self.rng.choice([
                    value + self.rng.uniform(100, 200),
                    value - self.rng.uniform(100, 200),
                ])

            rows.append({
                "id": i,
                "value": round(value, 2),
                "is_outlier": is_outlier,
            })

        return {
            "name": "outliers",
            "description": "Dataset with planted statistical outliers",
            "row_count": row_count,
            "columns": ["id", "value", "is_outlier"],
            "data": rows,
            "manifest": {
                "seed": self.seed,
                "planted_truths": {
                    "outlier_count": num_outliers,
                    "outlier_rate": round(num_outliers / row_count, 3),
                },
            },
        }

    def generate_missing_pattern_dataset(self, row_count: int = 1000, missing_rate: float = 0.1) -> dict[str, Any]:
        """Generate dataset with missing values for pattern detection testing.

        Args:
            num_rows: Number of rows.
            missing_rate: Fraction of values to miss.

        Returns:
            Dictionary with dataset and missing value information.
        """
        rows = []

        for i in range(row_count):
            value = self.rng.gauss(100, 15)
            category = self.rng.choice(["A", "B", "C"])

            # Randomly introduce missing values (MCAR - Missing Completely At Random)
            if self.rng.random() < missing_rate:
                value = None
            if self.rng.random() < missing_rate:
                category = None

            rows.append({
                "id": i,
                "value": round(value, 2) if value is not None else None,
                "category": category,
            })

        missing_value_count = sum(1 for r in rows if r["value"] is None)
        missing_category_count = sum(1 for r in rows if r["category"] is None)

        return {
            "name": "missing_mcar",
            "description": "Dataset with MCAR missing values",
            "row_count": row_count,
            "columns": ["id", "value", "category"],
            "data": rows,
            "manifest": {
                "seed": self.seed,
                "planted_truths": {
                    "pattern": "MCAR",
                    "missing_value_count": missing_value_count,
                    "missing_category_count": missing_category_count,
                    "total_missing": missing_value_count + missing_category_count,
                },
            },
        }

    def generate_all_datasets(self, output_dir: str) -> None:
        """Generate all golden datasets to output directory.

        Args:
            output_dir: Directory to save datasets.
        """
        from pathlib import Path  # noqa: PLC0415

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        datasets = [
            ("duplicates", self.generate_duplicate_dataset()),
            ("outliers", self.generate_outlier_dataset()),
            ("missing_mcar", self.generate_missing_pattern_dataset()),
        ]

        for name, dataset in datasets:
            dataset_dir = output_path / name
            dataset_dir.mkdir(exist_ok=True)

            # Save dataset
            data_file = dataset_dir / "data.json"
            data_file.write_text(json.dumps(dataset, indent=2))

            # Save manifest
            manifest = {
                "seed": self.seed,
                "planted_truths": dataset.get("manifest", {}).get("planted_truths", {}),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            manifest_file = dataset_dir / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))

    def save(self, dataset: dict[str, Any], output_dir: Path) -> Path:
        """Save dataset to JSON file.

        Args:
            dataset: Dataset dictionary.
            output_dir: Output directory path.

        Returns:
            Path to saved file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{dataset['name'].lower().replace(' ', '_')}.json"
        output_file.write_text(json.dumps(dataset, indent=2))
        return output_file


def main() -> None:
    """Generate all golden datasets."""
    generator = GoldenDatasetGenerator()
    output_dir = Path(__file__).parent / "datasets"

    datasets = [
        generator.generate_sales_dataset(),
        generator.generate_customer_churn_dataset(),
        generator.generate_anomaly_dataset(),
    ]

    for dataset in datasets:
        path = generator.save(dataset, output_dir)
        print(f"Generated: {path}")

    print(f"\nGenerated {len(datasets)} golden datasets in {output_dir}")


if __name__ == "__main__":
    main()
