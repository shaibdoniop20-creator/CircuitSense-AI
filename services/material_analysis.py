"""
CircuitSense AI - Material Analysis Service
Scientifically defensible e-waste material analysis implementing Mode A (Reference-Based Estimation)
and Mode B (Insufficient Data Handling). Never fabricates chemical composition from RGB images.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class MaterialAnalysisService:
    """
    Analyzes circuit board hazardous material content and precious metal recovery potentials
    using rigorous empirical references and transparent scientific disclosures.
    """

    def __init__(self, references_path: Optional[Path] = None):
        self.references_path = references_path or (Config.DATA_DIR / "material_references.json")
        self.reference_data = self._load_references()

    def _load_references(self) -> Dict[str, Any]:
        """Loads material composition benchmarks."""
        if not self.references_path.exists():
            logger.error(f"Material reference file not found at {self.references_path}")
            return {"board_categories": {}, "reference_metadata": {}}

        try:
            with open(self.references_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load material reference dataset: {e}")
            return {"board_categories": {}, "reference_metadata": {}}

    def analyze_board_materials(
        self,
        board_category: str = "unknown",
        board_mass_grams: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes material analysis in either Mode A (Reference-Based) or Mode B (Insufficient Data).
        """
        normalized_category = (board_category or "unknown").lower().strip()
        boards = self.reference_data.get("board_categories", {})
        meta = self.reference_data.get("reference_metadata", {})

        board_info = boards.get(normalized_category, boards.get("unknown", {}))
        has_sufficient_data = board_info.get("has_sufficient_data", False)

        # MODE B: Insufficient Data
        if not has_sufficient_data or normalized_category == "unknown":
            return {
                "mode": "MODE_B_INSUFFICIENT_DATA",
                "mode_title": "Mode B: Insufficient Data for Chemical Mass Estimation",
                "board_category": normalized_category,
                "display_name": board_info.get("display_name", "Unspecified Electronic Circuit Board"),
                "can_estimate_percentage": False,
                "estimated_hazardous_percentage": None,
                "notice": (
                    "Hazardous-material percentage cannot be reliably estimated from this image alone. "
                    "2D optical RGB photography does not penetrate component encapsulation to measure chemical mass fractions."
                ),
                "reason_insufficient": board_info.get(
                    "reason_insufficient",
                    "Optical features cannot distinguish RoHS-compliant lead-free solder alloys from leaded alloys or measure resin bromine content."
                ),
                "required_laboratory_steps": board_info.get("required_tests", [
                    "Specify or classify the PCB category (Motherboard, GPU, Controller, Power Supply).",
                    "Conduct handheld X-Ray Fluorescence (XRF) spectrometry for heavy metals (Pb, Cd, Hg, Cr-VI, Br).",
                    "Weigh the complete circuit board on a gravimetric scale (grams) to compute physical mass fractions."
                ]),
                "regulatory_risk": board_info.get("regulatory_risk", "Indeterminate - Default to Precautionary Containment"),
                "reference_sources": meta.get("sources", []),
                "scientific_limitation": meta.get("scientific_limitation_notice", "")
            }

        # MODE A: Reference-Based Estimation
        mass_range = board_info.get("estimated_mass_range_grams", {})
        used_mass = board_mass_grams if (board_mass_grams and board_mass_grams > 0) else mass_range.get("typical", 500)
        haz_pct_data = board_info.get("hazardous_content_percentage", {})

        typical_pct = haz_pct_data.get("typical", 3.0)
        min_pct = haz_pct_data.get("min", 2.0)
        max_pct = haz_pct_data.get("max", 5.0)

        # Defensible mass calculation:
        # Estimated Hazardous Mass = (typical_pct / 100) * total_mass
        est_hazardous_mass_g = round((typical_pct / 100.0) * used_mass, 2)
        est_hazardous_mass_min_g = round((min_pct / 100.0) * used_mass, 2)
        est_hazardous_mass_max_g = round((max_pct / 100.0) * used_mass, 2)

        return {
            "mode": "MODE_A_REFERENCE_BASED",
            "mode_title": "Mode A: Reference-Based Composition Estimate",
            "board_category": normalized_category,
            "display_name": board_info.get("display_name", normalized_category.title()),
            "can_estimate_percentage": True,
            "estimated_board_mass_grams": used_mass,
            "mass_source": "User-supplied" if board_mass_grams else "Empirical category benchmark typical mass",
            "estimated_hazardous_percentage": {
                "typical": typical_pct,
                "min": min_pct,
                "max": max_pct,
                "formatted": f"{min_pct}% - {max_pct}% (Typical: {typical_pct}%)"
            },
            "estimated_hazardous_mass_grams": {
                "typical": est_hazardous_mass_g,
                "min": est_hazardous_mass_min_g,
                "max": est_hazardous_mass_max_g,
                "formatted": f"{est_hazardous_mass_min_g}g - {est_hazardous_mass_max_g}g"
            },
            "formula_applied": "Hazardous Material Mass % = (Estimated Hazardous Substance Mass / Board Mass) × 100",
            "hazardous_substances": board_info.get("hazardous_substances", []),
            "valuable_fractions": board_info.get("valuable_fractions", {}),
            "regulatory_risk": haz_pct_data.get("regulatory_risk", "Moderate"),
            "handling_recommendations": board_info.get("handling_recommendations", []),
            "assumptions": [
                f"Board classified as '{board_info.get('display_name')}'.",
                f"Assumed baseline dry board mass of {used_mass}g.",
                "Chemical fraction ranges calibrated against UNEP & EMPA e-waste disassembly studies.",
                "Values represent statistical industry benchmarks rather than certified non-destructive laboratory testing."
            ],
            "reference_sources": meta.get("sources", []),
            "scientific_limitation": meta.get("scientific_limitation_notice", "")
        }
