"""
CircuitSense AI - Component Reusability & Triage Engine
Evaluates which detected PCB components can be safely reused, which require bench testing,
and which cannot be reused and must be routed to certified material recycling.
"""

from typing import Dict, Any, List

REUSABILITY_RULES = {
    "integrated_circuit": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 88,
        "action": "Harvest & Clean Leads",
        "reason": (
            "Solid-state silicon logic package. High secondary reliability if desoldered within "
            "thermal limits (<245°C) and pins remain unoxidized and straight."
        ),
        "risks": "Thermal stress during desoldering; verify pin continuity.",
        "secondary_demand": "High demand in educational maker kits, DIY electronics, and appliance repair depots."
    },
    "microcontroller": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 85,
        "action": "Erase Firmware & Pin Test",
        "reason": (
            "Programmable processing core (ARM Cortex / AVR / PIC). Intact package can be reprogrammed "
            "and deployed in secondary IoT or embedded prototyping projects."
        ),
        "risks": "Security fuses or locked bootloader may require hardware wipe.",
        "secondary_demand": "Very high salvage value for repair and educational prototyping."
    },
    "transistor": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-purple",
        "hex_color": "#B388FF",
        "base_score": 87,
        "action": "Multimeter Diode / Gain Test",
        "reason": (
            "Discrete three-terminal silicon semiconductor (BJT/MOSFET). Highly durable solid-state "
            "package. High secondary recovery value if desoldered within thermal limits (<250°C) "
            "and junction diodes verify proper PN forward voltage drop."
        ),
        "risks": "ESD sensitivity on gate oxide of MOSFETs; verify gate-to-source isolation.",
        "secondary_demand": "High demand in audio amplifier repairs, power supply refurbishment, and maker switching circuits."
    },
    "connector": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 92,
        "action": "Visual Inspection & Re-pin",
        "reason": (
            "Durable mechanical header / terminal block. Intact gold/tin plating and unmelted "
            "plastic housing make it immediately reusable in breadboards and enclosures."
        ),
        "risks": "Bent pin contacts or cracked plastic tongue.",
        "secondary_demand": "Standard utility across prototyping and hardware repair."
    },
    "capacitor": {
        "status": "recycle_only",
        "label": "Cannot Be Used Again (Recycle Only)",
        "badge_class": "badge-danger",
        "hex_color": "#E74C3C",
        "base_score": 25,
        "action": "Depollute & Recycle for Metal",
        "reason": (
            "Aged aluminum electrolytic capacitor. Liquid electrolyte dries out over 3-8 years, causing "
            "high Equivalent Series Resistance (ESR) drift, leakage currents, and risk of blowout. "
            "NOT recommended for reuse in operational circuits."
        ),
        "risks": "Capacitive degradation, dielectric breakdown, chemical electrolyte leak.",
        "secondary_demand": "Low component resale value; route to certified WEEE scrap recycler for aluminum reclamation."
    },
    "resistor": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 95,
        "action": "Multimeter Resistance Check",
        "reason": (
            "Passive thick-film or metal-film resistor. Negligible aging degradation; immediately "
            "reusable if resistance measures within rated tolerance (1% to 5%)."
        ),
        "risks": "Overheating discoloration or termination solder fracturing.",
        "secondary_demand": "Universal salvage utility across electronic prototyping and repair."
    },
    "diode": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 89,
        "action": "Diode Forward Drop Test",
        "reason": (
            "Discrete silicon junction rectifier or TVS diode. High solid-state durability if forward "
            "voltage measures ~0.6V (Si) or ~0.3V (Schottky) and reverse leakage is near zero."
        ),
        "risks": "Reverse breakdown damage from voltage spikes.",
        "secondary_demand": "High demand for secondary power conversion and DIY electronics."
    },
    "led": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 90,
        "action": "Low-Current Optical Test",
        "reason": (
            "Solid-state photonic indicator. 50,000+ hour operational lifespan with minimal degradation; "
            "easily verified with 3V coin cell battery."
        ),
        "risks": "Overcurrent bonding wire burnout.",
        "secondary_demand": "Popular in educational kits, maker boards, and indicator refurbishment."
    },
    "switch": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 86,
        "action": "Actuation & Contact Test",
        "reason": (
            "Tactile electromechanical switch or DIP toggle. Readily reusable if actuation click is firm "
            "and contact resistance measures below 1 ohm."
        ),
        "risks": "Contact oxidation or internal spring fatigue.",
        "secondary_demand": "Widely salvaged for keyboard, remote control, and appliance repair."
    },
    "inductor": {
        "status": "can_reuse",
        "label": "Can Be Used Again",
        "badge_class": "badge-green",
        "hex_color": "#2ECC71",
        "base_score": 94,
        "action": "Continuity & Inductance Check",
        "reason": (
            "Copper winding on ferrite core. Completely passive with no moving or chemical components; "
            "virtually unlimited operational lifespan when enamel is intact."
        ),
        "risks": "Cracked ferrite core or damaged winding enamel.",
        "secondary_demand": "High value in DC-DC buck converter and SMPS filter refurbishment."
    }
}



class ReusabilityService:
    """
    Evaluates individual and aggregate component reusability profiles.
    """

    @staticmethod
    def evaluate_component(
        component: Dict[str, Any],
        board_condition: str = "intact"
    ) -> Dict[str, Any]:
        """
        Assesses a single detected component and assigns actionable reusability classifications.
        """
        cls_name = component.get("class_name", "integrated_circuit")
        conf = component.get("confidence", 0.8)

        rule = REUSABILITY_RULES.get(cls_name, REUSABILITY_RULES["integrated_circuit"])

        status = rule["status"]
        score = rule["base_score"]
        label = rule["label"]
        badge_class = rule["badge_class"]
        reason = rule["reason"]
        action = rule["action"]

        # Board condition impact
        cond = (board_condition or "intact").lower()
        if cond in ("damaged", "corroded"):
            if status == "can_reuse":
                status = "needs_testing"
                label = "Inspect & Test First"
                badge_class = "badge-amber"
                score -= 30
                reason = f"Board condition is {cond.capitalize()}. Solder oxidation or physical stress requires multimeter and pin verification before reuse."
                action = "Microscope Pin & Continuity Check"
            elif status == "recycle_only":
                score = max(5, score - 15)
                reason += f" Severe risk due to {cond} board state."

        # Adjust score by confidence
        score = int(round(score * (0.85 + (conf * 0.15))))

        return {
            "status": status,
            "label": label,
            "badge_class": badge_class,
            "score": max(5, min(99, score)),
            "action": action,
            "reason": reason,
            "risks": rule.get("risks", "Standard electronic salvage risk."),
            "secondary_demand": rule.get("secondary_demand", "Secondary market utility.")
        }

    @staticmethod
    def summarize_triage(
        detections: List[Dict[str, Any]],
        board_condition: str = "intact"
    ) -> Dict[str, Any]:
        """
        Builds aggregate triage metrics: Can Reuse, Needs Testing, and Recycle Only.
        """
        can_reuse_count = 0
        needs_testing_count = 0
        recycle_only_count = 0

        can_reuse_items = []
        needs_testing_items = []
        recycle_only_items = []

        total = len(detections)

        for det in detections:
            eval_info = ReusabilityService.evaluate_component(det, board_condition)
            det["reusability"] = eval_info

            st = eval_info["status"]
            if st == "can_reuse":
                can_reuse_count += 1
                can_reuse_items.append(det)
            elif st == "needs_testing":
                needs_testing_count += 1
                needs_testing_items.append(det)
            else:
                recycle_only_count += 1
                recycle_only_items.append(det)

        can_reuse_pct = round((can_reuse_count / total * 100), 1) if total > 0 else 0.0
        needs_testing_pct = round((needs_testing_count / total * 100), 1) if total > 0 else 0.0
        recycle_only_pct = round((recycle_only_count / total * 100), 1) if total > 0 else 0.0

        # Overall Board Salvage Yield Score (0 - 100)
        salvage_score = int(round((can_reuse_pct * 1.0) + (needs_testing_pct * 0.5))) if total > 0 else 0

        return {
            "total_evaluated": total,
            "can_reuse_count": can_reuse_count,
            "can_reuse_pct": can_reuse_pct,
            "needs_testing_count": needs_testing_count,
            "needs_testing_pct": needs_testing_pct,
            "recycle_only_count": recycle_only_count,
            "recycle_only_pct": recycle_only_pct,
            "salvage_score": salvage_score,
            "can_reuse_items": can_reuse_items,
            "needs_testing_items": needs_testing_items,
            "recycle_only_items": recycle_only_items
        }
