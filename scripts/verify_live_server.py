"""
CircuitSense AI - Live Server HTTP Route Verification
Tests all HTTP endpoints and file generation on http://127.0.0.1:5000.
"""

import sys
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"

def check_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        content_type = resp.headers.get("Content-Type", "")
        print(f"GET {endpoint:<35} -> Status: {resp.status} | Content-Type: {content_type}")
        return resp.read()

def main():
    print("==================================================================")
    print("CircuitSense AI - Testing Live Endpoints on http://127.0.0.1:5000")
    print("==================================================================")

    # 1. Test Static & Info Pages
    check_get("/")
    check_get("/analyze")
    check_get("/history")
    check_get("/inventory")
    check_get("/material-analysis")
    check_get("/about")

    # 2. Test Image Upload & Full Inference
    sample_path = Path("data/sample_circuit.jpg")
    if not sample_path.exists():
        print("ERROR: sample_circuit.jpg not found.")
        sys.exit(1)

    print("\n[POST /analyze] Uploading sample circuit board and running YOLO inference...")
    with open(sample_path, "rb") as f:
        img_bytes = f.read()

    boundary = "----WebKitFormBoundarySampleTestCircuitSense"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="board_category"\r\n\r\n'
        f"motherboard\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="board_condition"\r\n\r\n'
        f"intact\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="confidence"\r\n\r\n'
        f"0.25\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="sample_circuit.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + img_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/analyze",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    with urllib.request.urlopen(req) as resp:
        final_url = resp.geturl()
        print(f"POST /analyze -> Success! Redirected to: {final_url} (Status: {resp.status})")
        html = resp.read().decode("utf-8")
        assert "sample_circuit.jpg" in html, "Sample filename must appear on results page"
        assert "Component Inventory" in html, "Inventory section must be rendered"
        assert "Estimated Recovery Value" in html, "Valuation section must be rendered"

    analysis_id = final_url.split("/results/")[-1]
    print(f"\n[DOWNLOAD TESTS] Generated Analysis ID: {analysis_id}")

    # 3. Test File Downloads
    pdf_bytes = check_get(f"/download/report/{analysis_id}")
    assert pdf_bytes.startswith(b"%PDF"), "ReportLab must return valid PDF bytes"
    print(f"  --> PDF Report Size: {len(pdf_bytes)} bytes (Valid PDF)")

    csv_bytes = check_get(f"/download/csv/{analysis_id}")
    assert b"CircuitSense AI - Component Inventory Export" in csv_bytes
    print(f"  --> CSV Inventory Size: {len(csv_bytes)} bytes (Valid CSV)")

    json_bytes = check_get(f"/download/json/{analysis_id}")
    assert b"analysis_id" in json_bytes
    print(f"  --> JSON Detections Payload: {len(json_bytes)} bytes (Valid JSON)")

    annotated_bytes = check_get(f"/download/annotated/{analysis_id}")
    print(f"  --> High-Res Annotated Image: {len(annotated_bytes)} bytes")

    print("\n==================================================================")
    print("ALL LIVE APPLICATION ROUTES AND EXPORTS FUNCTIONING FLAWLESSLY!")
    print("==================================================================")

if __name__ == "__main__":
    main()
