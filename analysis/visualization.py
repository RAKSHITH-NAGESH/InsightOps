import os

import matplotlib.pyplot as plt

from analysis.csv_loader import load_csv


def create_group_chart(
    file_path: str,
    category_column: str,
    metric_column: str,
    output_path: str,
) -> str:
    """
    Create a bar chart showing a metric
    grouped by category.
    """

    df = load_csv(file_path)

    grouped = (
        df.groupby(
            category_column,
            dropna=False
        )[metric_column]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    plt.figure(figsize=(9, 5))

    grouped.plot(
        kind="bar"
    )

    plt.title(
        f"{metric_column} by "
        f"{category_column}"
    )

    plt.xlabel(
        category_column
    )

    plt.ylabel(
        metric_column
    )

    plt.xticks(
        rotation=0
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return output_path


def create_scatter_chart(
    file_path: str,
    x_column: str,
    y_column: str,
    output_path: str,
) -> str:
    """
    Create a scatter plot between
    two numeric columns.
    """

    df = load_csv(file_path)

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    plt.figure(figsize=(9, 5))

    plt.scatter(
        df[x_column],
        df[y_column]
    )

    plt.title(
        f"{y_column} vs {x_column}"
    )

    plt.xlabel(
        x_column
    )

    plt.ylabel(
        y_column
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return output_path


def create_profit_margin_chart(
    file_path: str,
    category_column: str,
    revenue_column: str,
    profit_column: str,
    output_path: str,
) -> str:
    """
    Create a profit-margin chart
    grouped by category.
    """

    df = load_csv(file_path)

    grouped = (
        df.groupby(
            category_column,
            dropna=False
        )[
            [
                revenue_column,
                profit_column,
            ]
        ]
        .sum()
    )

    grouped["profit_margin"] = (
        grouped[profit_column]
        / grouped[revenue_column]
        * 100
    )

    grouped = grouped[
        "profit_margin"
    ].sort_values(
        ascending=False
    )

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    plt.figure(figsize=(9, 5))

    grouped.plot(
        kind="bar"
    )

    plt.title(
        f"Profit Margin by "
        f"{category_column}"
    )

    plt.xlabel(
        category_column
    )

    plt.ylabel(
        "Profit Margin (%)"
    )

    plt.xticks(
        rotation=0
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return output_path