"""
Live HTTP verification script for CircuitSense AI camera endpoints.
"""
import urllib.request
import json
import base64
from pathlib import Path

def test_endpoints():
    base_url = "http://127.0.0.1:5000"

    # 1. Test GET /analyze
    with urllib.request.urlopen(f"{base_url}/analyze") as res:
        html = res.read().decode("utf-8")
        assert "modeUploadBtn" in html, "Mode A button missing"
        assert "modeCameraBtn" in html, "Mode B button missing"
        assert "cameraVideo" in html, "cameraVideo element missing"
        assert "cameraCanvas" in html, "cameraCanvas element missing"
        assert "continuousDetectToggle" in html, "continuousDetectToggle missing"
        assert "camera.js" in html, "camera.js script tag missing"
        print("--> 1. GET /analyze rendered successfully with Mode A and Mode B!")

    # 2. Test GET /api/model-status
    with urllib.request.urlopen(f"{base_url}/api/model-status") as res:
        data = json.loads(res.read().decode("utf-8"))
        assert data["status"] == "success"
        print("--> 2. GET /api/model-status returned:", data["model_status"]["model_name"])

    # 3. Test POST /api/detect-frame with real motherboard sample
    uploads = list(Path("uploads").glob("*.jpeg")) + list(Path("uploads").glob("*.jpg"))
    sample_img = uploads[0]
    with open(sample_img, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/api/detect-frame",
        data=json.dumps({"frame": b64, "confidence": 0.25, "return_annotated": True}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        det_data = json.loads(res.read().decode("utf-8"))
        assert det_data["status"] == "success"
        print(f"--> 3. POST /api/detect-frame: Detected {det_data['total_components']} components in {det_data['inference_ms']} ms!")
        print(f"     Component counts: {det_data['component_counts']}")
        print(f"     Annotated frame data length: {len(det_data['annotated_frame'])} characters")

    # 4. Test POST /analyze with camera frame (JSON)
    req_analyze = urllib.request.Request(
        f"{base_url}/analyze",
        data=json.dumps({
            "camera_frame": b64,
            "board_category": "motherboard",
            "board_condition": "intact",
            "confidence": 0.25
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_analyze) as res:
        analysis_resp = json.loads(res.read().decode("utf-8"))
        assert analysis_resp["status"] == "success"
        print(f"--> 4. POST /analyze (camera_frame): Created analysis ID {analysis_resp['analysis_id']}")
        print(f"     Redirect URL: {analysis_resp['redirect_url']}")

    # 5. Test results page of the camera analysis
    results_url = f"{base_url}{analysis_resp['redirect_url']}"
    with urllib.request.urlopen(results_url) as res:
        res_html = res.read().decode("utf-8")
        assert "Component Reusability & Salvage Triage" in res_html
        print(f"--> 5. GET {results_url}: Results page rendered successfully with reusability & valuation!")

    print("\n================ ALL LIVE HTTP ENDPOINT TESTS PASSED! ================\n")

if __name__ == "__main__":
    test_endpoints()
