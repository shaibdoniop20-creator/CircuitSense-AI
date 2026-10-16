"""
CircuitSense AI - Synthetic Circuit Board Image Generator
Creates a sample circuit board photograph with realistic PCB traces, IC chips,
microcontroller package, electrolytic capacitors, and pin headers for offline testing.
"""

from pathlib import Path
import cv2
import numpy as np

def generate_sample_pcb(output_path: Path):
    w, h = 960, 720
    # Dark green FR-4 substrate background
    img = np.full((h, w, 3), (25, 65, 30), dtype=np.uint8)

    # Add subtle copper trace lines
    trace_color = (40, 110, 50)
    for i in range(20, w, 40):
        cv2.line(img, (i, 0), (i, h), trace_color, 2)
    for j in range(20, h, 40):
        cv2.line(img, (0, j), (w, j), trace_color, 2)

    # Draw PCB silkscreen text
    cv2.putText(img, "CIRCUITSENSE AI - EVAL BOARD REV 2.4", (40, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 220, 200), 2, cv2.LINE_AA)
    cv2.putText(img, "GND", (880, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 220, 200), 1)

    # 1. Microcontroller: Large central dark QFP/QFN square chip
    mcu_x1, mcu_y1, mcu_w, mcu_h = 400, 280, 160, 160
    cv2.rectangle(img, (mcu_x1, mcu_y1), (mcu_x1 + mcu_w, mcu_y1 + mcu_h), (25, 25, 25), -1)
    cv2.rectangle(img, (mcu_x1, mcu_y1), (mcu_x1 + mcu_w, mcu_y1 + mcu_h), (80, 80, 80), 2)
    # Pins around MCU
    pin_color = (180, 180, 180)
    for p in range(mcu_x1 + 10, mcu_x1 + mcu_w - 10, 12):
        cv2.line(img, (p, mcu_y1), (p, mcu_y1 - 12), pin_color, 2)
        cv2.line(img, (p, mcu_y1 + mcu_h), (p, mcu_y1 + mcu_h + 12), pin_color, 2)
    for p in range(mcu_y1 + 10, mcu_y1 + mcu_h - 10, 12):
        cv2.line(img, (mcu_x1, p), (mcu_x1 - 12, p), pin_color, 2)
        cv2.line(img, (mcu_x1 + mcu_w, p), (mcu_x1 + mcu_w + 12, p), pin_color, 2)
    cv2.putText(img, "ARM CORTEX", (mcu_x1 + 18, mcu_y1 + 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

    # 2. Integrated Circuit: SOIC/DIP package on upper left
    ic1_x, ic1_y, ic1_w, ic1_h = 140, 180, 130, 90
    cv2.rectangle(img, (ic1_x, ic1_y), (ic1_x + ic1_w, ic1_y + ic1_h), (20, 20, 20), -1)
    cv2.rectangle(img, (ic1_x, ic1_y), (ic1_x + ic1_w, ic1_y + ic1_h), (90, 90, 90), 2)
    for p in range(ic1_x + 8, ic1_x + ic1_w - 8, 14):
        cv2.line(img, (p, ic1_y), (p, ic1_y - 10), pin_color, 2)
        cv2.line(img, (p, ic1_y + ic1_h), (p, ic1_y + ic1_h + 10), pin_color, 2)
    cv2.putText(img, "74HC595", (ic1_x + 20, ic1_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # 3. Integrated Circuit 2: Lower right
    ic2_x, ic2_y, ic2_w, ic2_h = 660, 420, 140, 85
    cv2.rectangle(img, (ic2_x, ic2_y), (ic2_x + ic2_w, ic2_y + ic2_h), (20, 20, 20), -1)
    cv2.rectangle(img, (ic2_x, ic2_y), (ic2_x + ic2_w, ic2_y + ic2_h), (90, 90, 90), 2)
    cv2.putText(img, "LM358", (ic2_x + 35, ic2_y + 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # 4. Capacitors: Radial cylinders & circle pads
    caps = [(180, 480, 38), (280, 500, 32), (720, 220, 42)]
    for cx, cy, radius in caps:
        # Outer can
        cv2.circle(img, (cx, cy), radius, (50, 50, 180), -1)
        cv2.circle(img, (cx, cy), radius, (180, 180, 220), 2)
        # Top vent cross
        cv2.line(img, (cx - radius // 2, cy), (cx + radius // 2, cy), (30, 30, 120), 2)
        cv2.line(img, (cx, cy - radius // 2), (cx, cy + radius // 2), (30, 30, 120), 2)
        cv2.putText(img, "C", (cx - 8, cy - radius - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 220, 200), 1)

    # 5. Connectors: Headers & external ports
    # USB/Power Port on left edge
    conn1_x, conn1_y, conn1_w, conn1_h = 20, 320, 80, 110
    cv2.rectangle(img, (conn1_x, conn1_y), (conn1_x + conn1_w, conn1_y + conn1_h), (180, 180, 190), -1)
    cv2.rectangle(img, (conn1_x, conn1_y), (conn1_x + conn1_w, conn1_y + conn1_h), (60, 60, 70), 2)
    cv2.putText(img, "USB-C", (conn1_x + 10, conn1_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 30), 1)

    # Pin Header block on top right
    conn2_x, conn2_y, conn2_w, conn2_h = 620, 90, 180, 55
    cv2.rectangle(img, (conn2_x, conn2_y), (conn2_x + conn2_w, conn2_y + conn2_h), (30, 30, 30), -1)
    cv2.rectangle(img, (conn2_x, conn2_y), (conn2_x + conn2_w, conn2_y + conn2_h), (100, 100, 100), 1)
    for p in range(conn2_x + 12, conn2_x + conn2_w - 6, 18):
        cv2.circle(img, (p, conn2_y + 18), 4, (20, 200, 240), -1)
        cv2.circle(img, (p, conn2_y + 36), 4, (20, 200, 240), -1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"Sample PCB test image generated at: {output_path}")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "sample_circuit.jpg"
    generate_sample_pcb(out)
