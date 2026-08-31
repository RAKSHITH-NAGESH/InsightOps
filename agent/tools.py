# agent/tools.py
from typing import Optional
import pandas as pd

from analysis.csv_loader import load_csv
from analysis.anomaly import (
    detect_iqr_anomalies,
    discount_profit_analysis,
)
from analysis.statistics import (
    numeric_summary,
    group_analysis,
    correlation_analysis,
    calculate_profit_margin,
)
from google.adk.tools import Tool


def analyze_dataset(file_path: str, metric_column: str = None) -> dict:
    """Analyze a dataset and return key statistics."""
    
    try:
        df = load_csv(file_path)
        
        result = {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include='number').columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object', 'category']).columns.tolist(),
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        
        if metric_column and metric_column in df.columns:
            result["metric_summary"] = {
                "mean": float(df[metric_column].mean()),
                "median": float(df[metric_column].median()),
                "min": float(df[metric_column].min()),
                "max": float(df[metric_column].max()),
                "std": float(df[metric_column].std()),
            }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def find_business_issues(file_path: str) -> dict:
    """Find potential business issues in the dataset."""
    
    try:
        df = load_csv(file_path)
        
        issues = []
        
        # Check for high missing values
        missing_cols = df.columns[df.isnull().sum() > len(df) * 0.1].tolist()
        if missing_cols:
            issues.append({
                "type": "high_missing_values",
                "columns": missing_cols,
                "description": f"Columns with >10% missing values: {missing_cols}"
            })
        
        # Check for negative values in numeric columns
        numeric_cols = df.select_dtypes(include='number').columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                issues.append({
                    "type": "negative_values",
                    "column": col,
                    "description": f"Column '{col}' has negative values"
                })
        
        # Check for duplicate rows
        duplicates = int(df.duplicated().sum())
        if duplicates > 0:
            issues.append({
                "type": "duplicate_rows",
                "count": duplicates,
                "description": f"Found {duplicates} duplicate rows"
            })
        
        return {
            "success": True,
            "issues": issues,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# Register tools for the agent
tools = [
    Tool(
        name="analyze_dataset",
        description="Analyze a dataset and return statistics",
        function=analyze_dataset
    ),
    Tool(
        name="detect_iqr_anomalies",
        description="Detect anomalies using IQR method",
        function=lambda file_path, metric_column: detect_iqr_anomalies(file_path, metric_column)
    ),
    Tool(
        name="discount_profit_analysis",
        description="Analyze relationship between discount and profit",
        function=lambda file_path, discount_col, profit_col: discount_profit_analysis(
            file_path, discount_col, profit_col
        )
    ),
    Tool(
        name="find_business_issues",
        description="Find potential business issues in dataset",
        function=find_business_issues
    ),
]