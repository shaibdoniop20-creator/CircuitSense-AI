"""
CircuitSense AI - Component Inventory Service
Groups detections, computes class quantities, confidence metrics, and formats inventory.
"""

from typing import List, Dict, Any
from config import Config
from services.reusability import ReusabilityService, REUSABILITY_RULES


class InventoryService:
    """
    Computes component counts, class distributions, average confidences,
    reusability triage assessments, and structured inventory tables.
    """

    @staticmethod
    def build_inventory(
        detections: List[Dict[str, Any]],
        confidence_threshold: float = 0.0,
        board_condition: str = "intact"
    ) -> Dict[str, Any]:
        """
        Processes raw model detections into a structured inventory summary.
        Filters by confidence_threshold if specified, and assigns reusability triage.
        """
        # Filter detections by threshold
        valid_detections = [
            d for d in detections
            if d.get("confidence", 0.0) >= confidence_threshold
        ]

        # Compute triage reusability summary and enrich detections
        triage_summary = ReusabilityService.summarize_triage(
            valid_detections,
            board_condition=board_condition
        )

        total_detected = len(valid_detections)
        target_classes = Config.TARGET_CLASSES
        class_meta = Config.CLASS_METADATA

        # Initialize grouping for all supported classes
        class_summary = {}
        for cls_name in target_classes:
            meta = class_meta.get(cls_name, {})
            rule = REUSABILITY_RULES.get(cls_name, REUSABILITY_RULES["integrated_circuit"])
            class_summary[cls_name] = {
                "class_name": cls_name,
                "display_name": meta.get("display_name", cls_name.title()),
                "short_name": meta.get("short_name", cls_name.upper()),
                "hex_color": meta.get("hex_color", "#35C6C0"),
                "reusability_status": rule["status"],
                "reusability_label": rule["label"],
                "reusability_badge": rule["badge_class"],
                "reusability_action": rule["action"],
                "quantity": 0,
                "confidence_sum": 0.0,
                "average_confidence": 0.0,
                "average_confidence_pct": 0.0,
                "min_confidence": 1.0 if total_detected > 0 else 0.0,
                "max_confidence": 0.0,
                "detections": []
            }

        # Populate summary from detections
        high_confidence_count = 0
        all_confidences = []

        for det in valid_detections:
            cls_name = det.get("class_name", "integrated_circuit")
            conf = det.get("confidence", 0.0)
            all_confidences.append(conf)

            if conf >= 0.75:
                high_confidence_count += 1

            if cls_name not in class_summary:
                # Handle unexpected class gracefully
                class_summary[cls_name] = {
                    "class_name": cls_name,
                    "display_name": cls_name.replace("_", " ").title(),
                    "short_name": cls_name[:4].upper(),
                    "hex_color": "#A6AFBB",
                    "quantity": 0,
                    "confidence_sum": 0.0,
                    "average_confidence": 0.0,
                    "average_confidence_pct": 0.0,
                    "min_confidence": 1.0,
                    "max_confidence": 0.0,
                    "detections": []
                }

            group = class_summary[cls_name]
            group["quantity"] += 1
            group["confidence_sum"] += conf
            group["min_confidence"] = min(group["min_confidence"], conf)
            group["max_confidence"] = max(group["max_confidence"], conf)
            group["detections"].append(det)

        # Compute averages per class
        unique_classes_present = 0
        classes_list = []

        for cls_name, group in class_summary.items():
            qty = group["quantity"]
            if qty > 0:
                unique_classes_present += 1
                avg_conf = group["confidence_sum"] / qty
                group["average_confidence"] = round(avg_conf, 4)
                group["average_confidence_pct"] = round(avg_conf * 100, 1)
                group["min_confidence"] = round(group["min_confidence"], 4)
                group["max_confidence"] = round(group["max_confidence"], 4)
            else:
                group["min_confidence"] = 0.0
                group["max_confidence"] = 0.0
                group["average_confidence"] = 0.0
                group["average_confidence_pct"] = 0.0

            classes_list.append(group)

        # Global average confidence
        overall_avg_conf = (
            sum(all_confidences) / len(all_confidences)
            if all_confidences else 0.0
        )

        return {
            "total_components": total_detected,
            "unique_classes_count": unique_classes_present,
            "overall_average_confidence": round(overall_avg_conf, 4),
            "overall_average_confidence_pct": round(overall_avg_conf * 100, 1),
            "high_confidence_count": high_confidence_count,
            "by_class": class_summary,
            "classes_list": classes_list,
            "detections": valid_detections,
            "triage_summary": triage_summary
        }
