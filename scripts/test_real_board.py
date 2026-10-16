"""
Test real circuit board image upload through the complete CircuitSense AI pipeline.
Tests detection, crops, reusability triage, valuation, and HTML rendering.
"""
import io
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app, db, AnalysisRecord

def test_real_board_image():
    # Find an uploaded circuit board image
    uploads_dir = Path("uploads")
    sample_images = list(uploads_dir.glob("*.jpeg")) + list(uploads_dir.glob("*.jpg"))
    if not sample_images:
        print("ERROR: No sample circuit board image found in uploads/")
        return False

    test_img_path = sample_images[0]
    print(f"--> Using circuit board image: {test_img_path.name}")
    print(f"--> File size: {test_img_path.stat().st_size / 1024:.1f} KB")

    with open(test_img_path, "rb") as f:
        img_bytes = f.read()

    client = app.test_client()

    # Post image to /analyze
    response = client.post(
        "/analyze",
        data={
            "image": (io.BytesIO(img_bytes), test_img_path.name),
            "board_category": "motherboard",
            "board_condition": "intact",
            "confidence": "0.25"
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    print(f"--> POST /analyze status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Extract latest AnalysisRecord from database
    with app.app_context():
        latest = AnalysisRecord.query.order_by(AnalysisRecord.created_at.desc()).first()
        assert latest is not None, "No AnalysisRecord found in database!"
        
        data = latest.to_dict()
        analysis_id = data["analysis_id"]
        total_comps = data["total_components"]
        unique_classes = data["unique_classes"]
        val_mid = data["val_total_mid"]
        inv = data["inventory_summary"]
        triage = inv.get("triage_summary", {})

        print("\n=================== TEST RESULTS ===================")
        print(f"Analysis ID: {analysis_id}")
        print(f"Total Components Detected: {total_comps}")
        print(f"Unique Component Classes: {unique_classes}")
        print(f"Annotated Image Output: {data['annotated_filename']}")
        print(f"Estimated Recovery Value: Rs. {val_mid}")
        
        print("\n--- DETECTED COMPONENTS BREAKDOWN ---")
        for cls_item in inv.get("classes_list", []):
            if cls_item["quantity"] > 0:
                print(f"  * {cls_item['display_name']}: {cls_item['quantity']} detected (avg conf: {cls_item['average_confidence_pct']}%)")

        print("\n--- WHAT CAN BE USED AGAIN VS CANNOT BE USED AGAIN ---")
        print(f"  [CAN BE USED AGAIN]       : {triage.get('can_reuse_count', 0)} components ({triage.get('can_reuse_pct', 0.0)}%)")
        print(f"  [INSPECT & TEST FIRST]    : {triage.get('needs_testing_count', 0)} components ({triage.get('needs_testing_pct', 0.0)}%)")
        print(f"  [CANNOT BE USED AGAIN]    : {triage.get('recycle_only_count', 0)} components ({triage.get('recycle_only_pct', 0.0)}%)")
        print(f"  [BOARD SALVAGE YIELD]     : {triage.get('salvage_score', 0)} / 100")

        # Verify HTML response contains the new triage elements
        html = response.data.decode("utf-8")
        assert "Component Reusability & Salvage Triage" in html, "Triage section missing from HTML!"
        assert "Can Be Used Again" in html, "'Can Be Used Again' text missing from HTML!"
        assert "Cannot Be Used Again" in html, "'Cannot Be Used Again' text missing from HTML!"
        assert "Board Salvage Yield" in html, "'Board Salvage Yield' missing from HTML!"
        assert "crop-filter-btn" in html, "Crop filter tabs missing from HTML!"

        # Verify CSV export
        csv_resp = client.get(f"/download/csv/{analysis_id}")
        assert csv_resp.status_code == 200
        assert b"Reusability Status" in csv_resp.data
        print("\n--> CSV export verified with Reusability Status column!")

        # Verify PDF report
        pdf_resp = client.get(f"/download/report/{analysis_id}")
        assert pdf_resp.status_code == 200
        assert len(pdf_resp.data) > 1000
        print(f"--> PDF report generated successfully ({len(pdf_resp.data)} bytes)!")

        print("\n================ ALL CHECKS PASSED ================\n")
        return True

if __name__ == "__main__":
    success = test_real_board_image()
    sys.exit(0 if success else 1)
