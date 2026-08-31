import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def create_report(
    output_path: str,
    title: str,
    summary: str,
    findings: list,
    recommendations: list,
):
    """
    Generate an executive PDF report.
    """

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Executive Summary",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            str(summary),
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Key Findings",
            styles["Heading2"]
        )
    )

    finding_data = [
        ["#", "Finding"]
    ]

    for index, finding in enumerate(
        findings,
        start=1
    ):
        finding_data.append(
            [
                str(index),
                str(finding),
            ]
        )

    table = Table(
        finding_data,
        colWidths=[
            35,
            450,
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(table)

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Recommendations",
            styles["Heading2"]
        )
    )

    for recommendation in recommendations:

        story.append(
            Paragraph(
                f"• {recommendation}",
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 5)
        )

    document.build(story)