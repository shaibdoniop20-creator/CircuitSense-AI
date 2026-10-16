"""
CircuitSense AI - Component Valuation Service
Computes transparent, range-based market recovery valuations from detected components.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import Config
from services.reusability import REUSABILITY_RULES

logger = logging.getLogger(__name__)


class ValuationService:
    """
    Computes low-end, high-end, and midpoint secondary market valuations
    based on transparent reference catalogues and condition assumptions.
    """

    def __init__(self, catalogue_path: Optional[Path] = None):
        self.catalogue_path = catalogue_path or (Config.DATA_DIR / "component_prices.json")
        self.catalogue = self._load_catalogue()

    def _load_catalogue(self) -> Dict[str, Any]:
        """Loads the component pricing catalogue."""
        if not self.catalogue_path.exists():
            logger.error(f"Pricing catalogue not found at {self.catalogue_path}")
            return {"categories": {}, "catalogue_metadata": {}}

        try:
            with open(self.catalogue_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load pricing catalogue: {e}")
            return {"categories": {}, "catalogue_metadata": {}}

    def calculate_valuation(
        self,
        inventory_summary: Dict[str, Any],
        board_condition: str = "intact",
        selected_subtypes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates low, high, and midpoint secondary market recovery value.
        Condition adjustment factors:
        - intact: 1.0 (standard salvage assumption)
        - dismantled: 0.85 (handling wear)
        - damaged: 0.40 (mechanical risk, requiring extra testing)
        - corroded: 0.20 (chemical degradation, heavy testing required)
        """
        selected_subtypes = selected_subtypes or {}
        categories_data = self.catalogue.get("categories", {})
        meta = self.catalogue.get("catalogue_metadata", {})
        currency = meta.get("currency", Config.CURRENCY)
        currency_symbol = meta.get("currency_symbol", Config.CURRENCY_SYMBOL)

        condition_multipliers = {
            "intact": 1.0,
            "dismantled": 0.85,
            "damaged": 0.40,
            "corroded": 0.20
        }
        condition_factor = condition_multipliers.get(board_condition.lower(), 1.0)

        total_low = 0.0
        total_high = 0.0
        total_reusable_count = 0
        salvageable_mid = 0.0
        recycle_scrap_mid = 0.0
        per_class_breakdown = []
        unpriced_components = []

        by_class = inventory_summary.get("by_class", {})

        for cls_name, group in by_class.items():
            quantity = group.get("quantity", 0)
            if quantity == 0:
                continue

            pricing_cat = categories_data.get(cls_name)
            rule = REUSABILITY_RULES.get(cls_name, REUSABILITY_RULES["integrated_circuit"])

            if not pricing_cat:
                unpriced_components.append({
                    "class_name": cls_name,
                    "display_name": group.get("display_name", cls_name),
                    "quantity": quantity,
                    "reason": "No pricing benchmark found in catalogue for this component category."
                })
                continue

            subtypes = pricing_cat.get("subtypes", {})
            default_subtype_key = pricing_cat.get("default_subtype", list(subtypes.keys())[0] if subtypes else None)
            chosen_subtype_key = selected_subtypes.get(cls_name, default_subtype_key)
            subtype_info = subtypes.get(chosen_subtype_key, {})

            if not subtype_info:
                unpriced_components.append({
                    "class_name": cls_name,
                    "display_name": group.get("display_name", cls_name),
                    "quantity": quantity,
                    "reason": "Insufficient subtype pricing data."
                })
                continue

            unit_min = subtype_info.get("min_price_inr", 0.0)
            unit_max = subtype_info.get("max_price_inr", 0.0)
            unit_mid = (unit_min + unit_max) / 2.0

            # Apply condition factor
            adj_unit_min = round(unit_min * condition_factor, 2)
            adj_unit_max = round(unit_max * condition_factor, 2)
            adj_unit_mid = round(unit_mid * condition_factor, 2)

            class_subtotal_low = round(adj_unit_min * quantity, 2)
            class_subtotal_high = round(adj_unit_max * quantity, 2)
            class_subtotal_mid = round(adj_unit_mid * quantity, 2)

            total_low += class_subtotal_low
            total_high += class_subtotal_high
            total_reusable_count += quantity

            if rule["status"] in ("can_reuse", "needs_testing"):
                salvageable_mid += class_subtotal_mid
            else:
                recycle_scrap_mid += class_subtotal_mid

            per_class_breakdown.append({
                "class_name": cls_name,
                "display_name": group.get("display_name", cls_name),
                "short_name": group.get("short_name", cls_name[:3].upper()),
                "hex_color": group.get("hex_color", "#35C6C0"),
                "reusability_status": rule["status"],
                "reusability_label": rule["label"],
                "reusability_badge": rule["badge_class"],
                "reusability_action": rule["action"],
                "quantity": quantity,
                "subtype_key": chosen_subtype_key,
                "subtype_name": subtype_info.get("name", chosen_subtype_key),
                "available_subtypes": [
                    {"key": k, "name": v.get("name", k)}
                    for k, v in subtypes.items()
                ],
                "base_unit_range": f"{currency_symbol}{unit_min} - {currency_symbol}{unit_max}",
                "unit_low": adj_unit_min,
                "unit_high": adj_unit_max,
                "unit_mid": adj_unit_mid,
                "subtotal_low": class_subtotal_low,
                "subtotal_high": class_subtotal_high,
                "subtotal_mid": class_subtotal_mid,
                "source": subtype_info.get("source", "Illustrative demonstration data"),
                "condition_assumptions": subtype_info.get("condition_assumptions", "Standard salvage"),
                "reliability_note": subtype_info.get("reliability_note", "Visual detection only")
            })

        total_low = round(total_low, 2)
        total_high = round(total_high, 2)
        total_mid = round((total_low + total_high) / 2.0, 2)
        salvageable_mid = round(salvageable_mid, 2)
        recycle_scrap_mid = round(recycle_scrap_mid, 2)

        return {
            "currency": currency,
            "currency_symbol": currency_symbol,
            "board_condition": board_condition,
            "condition_factor": condition_factor,
            "total_low": total_low,
            "total_high": total_high,
            "total_mid": total_mid,
            "salvageable_mid": salvageable_mid,
            "recycle_scrap_mid": recycle_scrap_mid,
            "total_reusable_components": total_reusable_count,
            "breakdown": per_class_breakdown,
            "unpriced_components": unpriced_components,
            "catalogue_metadata": meta,
            "assumptions": [
                f"Board condition adjusted with factor {condition_factor}x ({board_condition.capitalize()}).",
                "Unit pricing assumes intact physical terminals without electrical shorts or silicon substrate rupture.",
                "Estimated value reflects salvage broker wholesale pricing, not retail consumer part replacement.",
                "Actual recovery value requires functional continuity bench testing and buyer demand."
            ]
        }
