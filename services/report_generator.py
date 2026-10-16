"""
CircuitSense AI - Report Generator Service
Generates comprehensive PDF audit reports using ReportLab and structured CSV inventory exports.
"""

import io
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, HRFlowable, KeepTogether
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Builds technical PDF analysis reports and CSV inventory exports.
    """

    @staticmethod
    def generate_inventory_csv(
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Exports the component detections into a standard CSV format.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header Metadata
        writer.writerow(["CircuitSense AI - Component Inventory Export"])
        writer.writerow(["Analysis ID", analysis_data.get("analysis_id", "N/A")])
        writer.writerow(["Source Image", analysis_data.get("original_filename", "N/A")])
        writer.writerow(["Timestamp", analysis_data.get("created_at", datetime.now().isoformat())])
        writer.writerow(["Board Category", analysis_data.get("board_category", "unknown")])
        writer.writerow(["Board Condition", analysis_data.get("board_condition", "intact")])
        writer.writerow([])

        # Table Header
        writer.writerow([
            "Detection ID",
            "Component Class",
            "Display Name",
            "Confidence Score",
            "Confidence %",
            "Reusability Status",
            "Triage Action",
            "Bounding Box (X1, Y1, X2, Y2)",
            "Detection Engine"
        ])

        detections = analysis_data.get("detections", [])
        for det in detections:
            bbox = det.get("bbox", {})
            bbox_str = f"({bbox.get('x1', 0)}, {bbox.get('y1', 0)}, {bbox.get('x2', 0)}, {bbox.get('y2', 0)})"
            reus = det.get("reusability", {})
            reus_status = reus.get("label", "Can Be Used Again" if det.get("class_name") != "capacitor" else "Cannot Be Used Again (Recycle Only)")
            reus_act = reus.get("action", "Inspect & Clean" if det.get("class_name") != "capacitor" else "Depollute for Metal Scrap")
            writer.writerow([
                det.get("detection_id", ""),
                det.get("class_name", ""),
                det.get("display_name", ""),
                det.get("confidence", 0.0),
                f"{det.get('confidence_pct', 0.0)}%",
                reus_status,
                reus_act,
                bbox_str,
                "Simulated Demo" if det.get("is_simulated") else "YOLOv8 Production"
            ])

        writer.writerow([])
        writer.writerow(["Component Reusability & Salvage Triage Summary"])
        inventory = analysis_data.get("inventory_summary", {})
        triage = inventory.get("triage_summary", {})
        writer.writerow(["Category", "Count", "Percentage", "Recommended Action"])
        writer.writerow(["Can Be Used Again", triage.get("can_reuse_count", 0), f"{triage.get('can_reuse_pct', 0.0)}%", "Harvest & Clean Leads"])
        writer.writerow(["Inspect & Test First", triage.get("needs_testing_count", 0), f"{triage.get('needs_testing_pct', 0.0)}%", "Microscope Pin & Continuity Check"])
        writer.writerow(["Cannot Be Used Again (Recycle Only)", triage.get("recycle_only_count", 0), f"{triage.get('recycle_only_pct', 0.0)}%", "Depollute & Route to Metal Recycler"])
        writer.writerow(["Board Salvage Yield Score", f"{triage.get('salvage_score', 0)} / 100", "-", "-"])

        writer.writerow([])
        writer.writerow(["Class Summary Aggregates"])
        writer.writerow(["Class Name", "Quantity", "Average Confidence", "Estimated Recoverable Midpoint (INR)"])

        valuation = analysis_data.get("valuation_summary", {})
        val_breakdown = {b["class_name"]: b for b in valuation.get("breakdown", [])}

        for item in inventory.get("classes_list", []):
            cls_name = item.get("class_name")
            val_info = val_breakdown.get(cls_name, {})
            writer.writerow([
                item.get("display_name"),
                item.get("quantity"),
                f"{item.get('average_confidence_pct')}%",
                f"Rs. {val_info.get('subtotal_mid', 0.0)}"
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf_report(
        analysis_data: Dict[str, Any],
        annotated_image_path: Optional[str] = None
    ) -> bytes:
        """
        Builds a multi-page, publication-grade PDF report with ReportLab.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom dark & clean palette styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#17191D")
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#5799F7")
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#20242B"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#2C3E50")
        )
        body_bold = ParagraphStyle(
            "BodyDarkBold",
            parent=body_style,
            fontName="Helvetica-Bold"
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor("#7F8C8D")
        )

        story = []

        # Header Banner
        header_table_data = [
            [
                Paragraph("<b>CircuitSense AI</b>", title_style),
                Paragraph(f"<b>ANALYSIS ID:</b> {analysis_data.get('analysis_id', 'N/A')}<br/>"
                          f"<b>DATE:</b> {datetime.now().strftime('%d %b %Y, %H:%M')}", body_style)
            ],
            [
                Paragraph("Intelligent E-Waste Circuit Component Classifier & Material Analyzer", subtitle_style),
                Paragraph(f"<b>STATUS:</b> {'SIMULATED DEMO' if analysis_data.get('is_demo') else 'VERIFIED YOLO'}", body_bold)
            ]
        ]
        header_table = Table(header_table_data, colWidths=[360, 180])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#35C6C0"), spaceAfter=12))

        # Executive Summary Box
        inv = analysis_data.get("inventory_summary", {})
        val = analysis_data.get("valuation_summary", {})
        mat = analysis_data.get("material_analysis", {})

        summary_data = [
            [
                Paragraph("<b>Source File:</b>", body_bold),
                Paragraph(str(analysis_data.get("original_filename", "N/A")), body_style),
                Paragraph("<b>Total Components:</b>", body_bold),
                Paragraph(str(inv.get("total_components", 0)), body_bold)
            ],
            [
                Paragraph("<b>Board Category:</b>", body_bold),
                Paragraph(str(analysis_data.get("board_category", "unknown")).title(), body_style),
                Paragraph("<b>Overall Confidence:</b>", body_bold),
                Paragraph(f"{inv.get('overall_average_confidence_pct', 0)}%", body_style)
            ],
            [
                Paragraph("<b>Board Condition:</b>", body_bold),
                Paragraph(str(analysis_data.get("board_condition", "intact")).capitalize(), body_style),
                Paragraph("<b>Recoverable Value:</b>", body_bold),
                Paragraph(f"₹{val.get('total_low', 0)} - ₹{val.get('total_high', 0)}", body_bold)
            ]
        ]
        sum_table = Table(summary_data, colWidths=[100, 170, 120, 150])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F4F6F8")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ECF0F1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 10))

        # Annotated Image Embedding
        if annotated_image_path and Path(annotated_image_path).exists():
            try:
                story.append(Paragraph("1. Computer Vision Detection Map", h2_style))
                # Max width 520, proportional height
                img_rl = ReportLabImage(annotated_image_path, width=520, height=230)
                story.append(img_rl)
                story.append(Paragraph("Visualized detection bounding boxes: Cyan=IC, Blue=Microcontroller, Violet=Transistor, Green=Capacitor, Amber=Connector.", disclaimer_style))
                story.append(Spacer(1, 10))
            except Exception as e:
                logger.error(f"Could not embed image in PDF: {e}")

        # 2. Component Reusability & Salvage Triage Section
        story.append(Paragraph("2. Component Reusability & Salvage Triage", h2_style))
        triage = inv.get("triage_summary", {})
        triage_table_data = [
            [
                Paragraph("<b>Triage Category</b>", body_bold),
                Paragraph("<b>Qty</b>", body_bold),
                Paragraph("<b>% Share</b>", body_bold),
                Paragraph("<b>Triage Action & Engineering Rationales</b>", body_bold)
            ],
            [
                Paragraph("<font color='#27AE60'><b>Can Be Used Again</b></font>", body_bold),
                Paragraph(str(triage.get("can_reuse_count", 0)), body_style),
                Paragraph(f"{triage.get('can_reuse_pct', 0.0)}%", body_style),
                Paragraph("<b>Action:</b> Harvest & Clean Leads. Solid-state logic ICs, MCUs, transistors, connectors with intact package integrity.", body_style)
            ],
            [
                Paragraph("<font color='#D68910'><b>Inspect & Test First</b></font>", body_bold),
                Paragraph(str(triage.get("needs_testing_count", 0)), body_style),
                Paragraph(f"{triage.get('needs_testing_pct', 0.0)}%", body_style),
                Paragraph("<b>Action:</b> Multimeter & Pin Verify. Test for oxidation or thermal damage before circuit reuse.", body_style)
            ],
            [
                Paragraph("<font color='#C0392B'><b>Cannot Reuse (Recycle Only)</b></font>", body_bold),
                Paragraph(str(triage.get("recycle_only_count", 0)), body_style),
                Paragraph(f"{triage.get('recycle_only_pct', 0.0)}%", body_style),
                Paragraph("<b>Action:</b> Depollute for Metal Scrap. Aged electrolytic capacitors dry out over 3-8 yrs; high ESR blowout risk.", body_style)
            ]
        ]
        triage_table = Table(triage_table_data, colWidths=[140, 45, 65, 290])
        triage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ]))
        story.append(triage_table)
        story.append(Paragraph(f"<b>Overall Board Salvage Yield Score:</b> {triage.get('salvage_score', 0)} / 100", body_style))
        story.append(Spacer(1, 10))

        # Component Inventory Table
        story.append(Paragraph("3. Detected Component Inventory", h2_style))
        inv_table_data = [
            [
                Paragraph("<b>Component Class</b>", body_bold),
                Paragraph("<b>Quantity</b>", body_bold),
                Paragraph("<b>Avg. Confidence</b>", body_bold),
                Paragraph("<b>Reusability Potential</b>", body_bold)
            ]
        ]

        for item in inv.get("classes_list", []):
            qty = item.get("quantity", 0)
            avg_c = item.get("average_confidence_pct", 0)
            reusability = "High (Check Pins)" if qty > 0 and avg_c >= 80 else ("Moderate" if qty > 0 else "None Detected")
            inv_table_data.append([
                Paragraph(item.get("display_name", ""), body_style),
                Paragraph(str(qty), body_style),
                Paragraph(f"{avg_c}%", body_style),
                Paragraph(reusability, body_style)
            ])

        inv_table = Table(inv_table_data, colWidths=[200, 90, 110, 140])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ]))
        story.append(inv_table)
        story.append(Spacer(1, 10))

        # Second-Hand Valuation Breakdown
        # Second-Hand Valuation Breakdown
        story.append(Paragraph("4. Second-Hand Market Value Estimation (INR)", h2_style))
        val_table_data = [
            [
                Paragraph("<b>Component Type</b>", body_bold),
                Paragraph("<b>Quantity</b>", body_bold),
                Paragraph("<b>Unit Range (₹)</b>", body_bold),
                Paragraph("<b>Subtotal Low (₹)</b>", body_bold),
                Paragraph("<b>Subtotal High (₹)</b>", body_bold),
                Paragraph("<b>Midpoint (₹)</b>", body_bold),
            ]
        ]

        for b in val.get("breakdown", []):
            val_table_data.append([
                Paragraph(b.get("display_name", ""), body_style),
                Paragraph(str(b.get("quantity", 0)), body_style),
                Paragraph(f"₹{b.get('unit_low')} - ₹{b.get('unit_high')}", body_style),
                Paragraph(f"₹{b.get('subtotal_low')}", body_style),
                Paragraph(f"₹{b.get('subtotal_high')}", body_style),
                Paragraph(f"₹{b.get('subtotal_mid')}", body_bold),
            ])

        # Total Row
        val_table_data.append([
            Paragraph("<b>TOTAL RECOVERABLE VALUE</b>", body_bold),
            Paragraph(f"<b>{val.get('total_reusable_components', 0)}</b>", body_bold),
            Paragraph("-", body_style),
            Paragraph(f"<b>₹{val.get('total_low', 0)}</b>", body_bold),
            Paragraph(f"<b>₹{val.get('total_high', 0)}</b>", body_bold),
            Paragraph(f"<b>₹{val.get('total_mid', 0)}</b>", body_bold),
        ])

        val_table = Table(val_table_data, colWidths=[160, 60, 100, 75, 75, 70])
        val_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#D5F5E3")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ]))
        story.append(val_table)
        story.append(Paragraph("<i>Valuation assumes unsoldered pins without silicon damage. Reflects secondary salvage depot wholesale pricing.</i>", disclaimer_style))
        story.append(Spacer(1, 10))

        # Material Analysis Section
        story.append(Paragraph("5. Material Composition & Hazardous Content Analysis", h2_style))
        if mat.get("can_estimate_percentage"):
            haz_pct = mat.get("estimated_hazardous_percentage", {})
            mat_text = (
                f"<b>Reference Category:</b> {mat.get('display_name')}<br/>"
                f"<b>Estimated Hazardous Substance Mass %:</b> {haz_pct.get('formatted')}<br/>"
                f"<b>Estimated Hazardous Mass:</b> {mat.get('estimated_hazardous_mass_grams', {}).get('formatted')} "
                f"(based on assumed dry board mass of {mat.get('estimated_board_mass_grams')}g)<br/>"
                f"<b>Regulatory Risk Level:</b> {mat.get('regulatory_risk')}"
            )
            story.append(Paragraph(mat_text, body_style))
        else:
            story.append(Paragraph(
                "<b>MODE B ASSESSMENT:</b> " + mat.get("notice", "Insufficient data for direct chemical estimation.") + "<br/>"
                "<i>RGB photographs cannot perform spectrometry or measure substrate resin bromine without laboratory XRF testing.</i>",
                body_style
            ))

        story.append(Spacer(1, 10))

        # Recommendations & Disclaimers
        story.append(Paragraph("6. Engineering Recommendations & Handling Guidelines", h2_style))
        recommendations = [
            "• Perform electrical in-circuit continuity testing and visual microscope pin inspection prior to resale.",
            "• Safely discharge all primary electrolytic capacitors with an insulated 1k-ohm bleed resistor prior to desoldering.",
            "• Use dedicated local exhaust ventilation (fume extraction) when desoldering to prevent exposure to lead/flux fumes.",
            "• Direct remaining FR-4 fiberglass substrate to certified WEEE pyrometallurgical refiners to reclaim precious metals."
        ]
        for rec in recommendations:
            story.append(Paragraph(rec, body_style))

        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"), spaceAfter=6))
        story.append(Paragraph(
            "<b>STATUTORY DISCLAIMER:</b> CircuitSense AI provides algorithmic visual classification and statistical reference benchmarks "
            "for decision support and educational research. Detections do not guarantee functional viability or commercial resale liquidity. "
            "Material estimates are derived from published empirical studies and must not replace certified laboratory chemical testing.",
            disclaimer_style
        ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
