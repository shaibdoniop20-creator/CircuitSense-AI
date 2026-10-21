"""
CircuitSense AI - Intelligent E-Waste Circuit Component Classifier & Material Analyzer
Main Flask Application & API Routes
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_from_directory, jsonify, abort, Response
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from services.detector import PCBDetector
from services.image_processor import ImageProcessor
from services.inventory import InventoryService
from services.valuation import ValuationService
from services.material_analysis import MaterialAnalysisService
from services.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("circuitsense")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure required directories exist
for folder in [
    Config.UPLOADS_DIR,
    Config.OUTPUTS_DIR,
    Config.CROPS_DIR,
    Config.DATA_DIR,
    Config.MODELS_DIR,
    Config.INSTANCE_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize singleton services
detector = PCBDetector()
valuation_service = ValuationService()
material_service = MaterialAnalysisService()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class AnalysisRecord(db.Model):
    """Stores persistent circuit board analysis history."""
    __tablename__ = "analysis_records"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    annotated_filename = db.Column(db.String(255), nullable=False)
    board_category = db.Column(db.String(50), default="unknown")
    board_condition = db.Column(db.String(50), default="intact")
    image_width = db.Column(db.Integer, default=0)
    image_height = db.Column(db.Integer, default=0)
    file_size_kb = db.Column(db.Float, default=0.0)
    model_mode = db.Column(db.String(50), default="demo")
    is_demo = db.Column(db.Boolean, default=True)
    total_components = db.Column(db.Integer, default=0)
    unique_classes = db.Column(db.Integer, default=0)
    overall_confidence = db.Column(db.Float, default=0.0)
    val_total_low = db.Column(db.Float, default=0.0)
    val_total_high = db.Column(db.Float, default=0.0)
    val_total_mid = db.Column(db.Float, default=0.0)
    material_mode = db.Column(db.String(50), default="MODE_B_INSUFFICIENT_DATA")
    hazardous_pct_typical = db.Column(db.Float, nullable=True)

    # Detailed serialized payloads
    detections_json = db.Column(db.Text, default="[]")
    inventory_json = db.Column(db.Text, default="{}")
    valuation_json = db.Column(db.Text, default="{}")
    material_json = db.Column(db.Text, default="{}")

    def to_dict(self) -> Dict[str, Any]:
        """Converts model to dictionary for views and API responses."""
        return {
            "analysis_id": self.analysis_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "annotated_filename": self.annotated_filename,
            "board_category": self.board_category,
            "board_condition": self.board_condition,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "file_size_kb": self.file_size_kb,
            "model_mode": self.model_mode,
            "is_demo": self.is_demo,
            "total_components": self.total_components,
            "unique_classes": self.unique_classes,
            "overall_confidence": self.overall_confidence,
            "val_total_low": self.val_total_low,
            "val_total_high": self.val_total_high,
            "val_total_mid": self.val_total_mid,
            "material_mode": self.material_mode,
            "hazardous_pct_typical": self.hazardous_pct_typical,
            "detections": json.loads(self.detections_json) if self.detections_json else [],
            "inventory_summary": json.loads(self.inventory_json) if self.inventory_json else {},
            "valuation_summary": json.loads(self.valuation_json) if self.valuation_json else {},
            "material_analysis": json.loads(self.material_json) if self.material_json else {}
        }


# Create database tables if they do not exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logger.debug(f"Table initialization notice: {e}")


# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_global_metadata():
    """Injects branding, model status, and navigation metadata into all templates."""
    return {
        "app_name": "CircuitSense AI",
        "app_subtitle": "Intelligent E-Waste Circuit Component Classifier & Material Analyzer",
        "app_tagline": "Detect Smarter. Recover More. Recycle Responsibly.",
        "currency_symbol": Config.CURRENCY_SYMBOL,
        "currency": Config.CURRENCY,
        "model_status": detector.get_model_status(),
        "target_classes_meta": Config.CLASS_METADATA,
        "current_year": datetime.now(timezone.utc).year
    }


# ============================================================================
# CORE APPLICATION ROUTES
# ============================================================================

@app.route("/")
def index():
    """Landing Page: Project overview, live metrics, and analysis entrypoint."""
    recent_analyses = AnalysisRecord.query.order_by(AnalysisRecord.created_at.desc()).limit(4).all()
    total_analyzed = AnalysisRecord.query.count()
    total_components_recovered = db.session.query(db.func.sum(AnalysisRecord.total_components)).scalar() or 0
    total_value_identified = db.session.query(db.func.sum(AnalysisRecord.val_total_mid)).scalar() or 0.0

    return render_template(
        "index.html",
        recent_analyses=[r.to_dict() for r in recent_analyses],
        total_analyzed=total_analyzed,
        total_components_recovered=int(total_components_recovered),
        total_value_identified=round(float(total_value_identified), 2)
    )


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Image upload and actual computer vision analysis pipeline."""
    if request.method == "GET":
        return render_template("upload.html")

    # POST: Process uploaded circuit board image
    if "image" not in request.files:
        flash("No image file provided in upload request.", "error")
        return redirect(url_for("analyze"))

    file = request.files["image"]
    if not file or file.filename == "":
        flash("Please select a circuit board image to analyze.", "error")
        return redirect(url_for("analyze"))

    # Optional metadata from form
    board_category = request.form.get("board_category", "unknown").strip().lower()
    board_condition = request.form.get("board_condition", "intact").strip().lower()
    confidence_thresh = float(request.form.get("confidence", Config.DEFAULT_CONFIDENCE))

    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    orig_filename_safe = secure_filename(file.filename) or f"circuit_{analysis_id[:8]}.jpg"
    stored_filename = f"{analysis_id}_{orig_filename_safe}"
    stored_path = Config.UPLOADS_DIR / stored_filename

    # Validate and save image safely
    is_valid, err_msg, img_meta = ImageProcessor.validate_and_save_upload(file, stored_path)
    if not is_valid:
        flash(f"Image validation failed: {err_msg}", "error")
        return redirect(url_for("analyze"))

    try:
        # Run actual detector inference
        detections, model_status = detector.detect(
            image_path=str(stored_path),
            confidence_threshold=confidence_thresh,
            iou_threshold=Config.DEFAULT_IOU
        )

        # Generate annotated output image
        annotated_filename = f"{analysis_id}_annotated.jpg"
        annotated_path = Config.OUTPUTS_DIR / annotated_filename
        _, img_w, img_h = ImageProcessor.render_annotated_image(
            original_image_path=str(stored_path),
            output_image_path=str(annotated_path),
            detections=detections,
            confidence_filter=0.0
        )

        # Extract individual component crops for high-detail inspection
        detections = ImageProcessor.generate_component_crops(
            original_image_path=str(stored_path),
            crops_dir=Config.CROPS_DIR,
            analysis_id=analysis_id,
            detections=detections
        )

        # Build inventory summary with reusability triage
        inventory_summary = InventoryService.build_inventory(
            detections,
            confidence_threshold=0.0,
            board_condition=board_condition
        )

        # Calculate second-hand market valuation
        valuation_summary = valuation_service.calculate_valuation(
            inventory_summary=inventory_summary,
            board_condition=board_condition
        )

        # Perform hazardous material & precious metal analysis
        material_analysis = material_service.analyze_board_materials(
            board_category=board_category
        )

        # Persist analysis to SQLite database
        typical_haz = (
            material_analysis.get("estimated_hazardous_percentage", {}).get("typical")
            if material_analysis.get("can_estimate_percentage") else None
        )

        record = AnalysisRecord(
            analysis_id=analysis_id,
            created_at=datetime.now(timezone.utc),
            original_filename=orig_filename_safe,
            stored_filename=stored_filename,
            annotated_filename=annotated_filename,
            board_category=board_category,
            board_condition=board_condition,
            image_width=img_w,
            image_height=img_h,
            file_size_kb=img_meta.get("file_size_kb", 0.0),
            model_mode=model_status.get("mode", "demo"),
            is_demo=model_status.get("is_demo", True),
            total_components=inventory_summary.get("total_components", 0),
            unique_classes=inventory_summary.get("unique_classes_count", 0),
            overall_confidence=inventory_summary.get("overall_average_confidence", 0.0),
            val_total_low=valuation_summary.get("total_low", 0.0),
            val_total_high=valuation_summary.get("total_high", 0.0),
            val_total_mid=valuation_summary.get("total_mid", 0.0),
            material_mode=material_analysis.get("mode", "MODE_B_INSUFFICIENT_DATA"),
            hazardous_pct_typical=typical_haz,
            detections_json=json.dumps(detections),
            inventory_json=json.dumps(inventory_summary),
            valuation_json=json.dumps(valuation_summary),
            material_json=json.dumps(material_analysis)
        )
        db.session.add(record)
        db.session.commit()

        # If AJAX submission requested JSON, return it; otherwise redirect
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.accept_mimetypes.best == "application/json":
            return jsonify({
                "status": "success",
                "analysis_id": analysis_id,
                "redirect_url": url_for("results", analysis_id=analysis_id)
            })

        return redirect(url_for("results", analysis_id=analysis_id))

    except Exception as e:
        logger.error(f"Analysis failed for {stored_filename}: {e}", exc_info=True)
        # Clean up uploaded file if failure occurred
        if stored_path.exists():
            try:
                stored_path.unlink()
            except Exception:
                pass
        flash(f"An error occurred during circuit board analysis: {str(e)}", "error")
        return redirect(url_for("analyze"))


@app.route("/results/<analysis_id>")
def results(analysis_id):
    """Interactive Analysis Results Dashboard."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        flash(f"Analysis with ID '{analysis_id}' was not found.", "error")
        return redirect(url_for("analyze"))

    data = record.to_dict()

    # Ensure triage summary is present (supports past records)
    inv_summary = data.get("inventory_summary", {})
    if "triage_summary" not in inv_summary:
        from services.reusability import ReusabilityService
        inv_summary["triage_summary"] = ReusabilityService.summarize_triage(
            data.get("detections", []),
            board_condition=data.get("board_condition", "intact")
        )
        data["inventory_summary"] = inv_summary

    return render_template("results.html", analysis=data)


@app.route("/history")
def history():
    """Analysis History: Review, search, and manage past evaluations."""
    query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip().lower()

    sql_query = AnalysisRecord.query

    if query:
        sql_query = sql_query.filter(
            (AnalysisRecord.original_filename.ilike(f"%{query}%")) |
            (AnalysisRecord.analysis_id.ilike(f"%{query}%"))
        )

    if category_filter and category_filter != "all":
        sql_query = sql_query.filter(AnalysisRecord.board_category == category_filter)

    records = sql_query.order_by(AnalysisRecord.created_at.desc()).all()
    return render_template(
        "history.html",
        records=[r.to_dict() for r in records],
        search_query=query,
        category_filter=category_filter,
        total_count=len(records)
    )


@app.route("/inventory")
def inventory_catalogue():
    """Component Inventory reference view and aggregate analytics."""
    records = AnalysisRecord.query.all()
    # Aggregate component counts across all previous analyses
    aggregate_counts = {cls: 0 for cls in Config.TARGET_CLASSES}
    total_detected_all = 0

    for rec in records:
        inv = json.loads(rec.inventory_json) if rec.inventory_json else {}
        for cls_name, info in inv.get("by_class", {}).items():
            if cls_name in aggregate_counts:
                qty = info.get("quantity", 0)
                aggregate_counts[cls_name] += qty
                total_detected_all += qty

    pricing_data = valuation_service.catalogue.get("categories", {})

    return render_template(
        "inventory.html",
        aggregate_counts=aggregate_counts,
        total_detected_all=total_detected_all,
        pricing_data=pricing_data
    )


@app.route("/material-analysis")
def material_analysis_info():
    """Material Analysis Methodology, Empirical References, and RoHS Standards."""
    refs = material_service.reference_data
    return render_template(
        "material_analysis.html",
        board_categories=refs.get("board_categories", {}),
        reference_metadata=refs.get("reference_metadata", {})
    )


@app.route("/about")
def about():
    """Project Details, YOLOv8 Architecture, Hackathon Objectives, and Model Connect Guide."""
    return render_template("about.html")


# ============================================================================
# EXPORT & DOWNLOAD ROUTES
# ============================================================================

@app.route("/download/report/<analysis_id>")
def download_pdf_report(analysis_id):
    """Generates and serves a publication-grade PDF report."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        abort(404, description="Analysis record not found.")

    data = record.to_dict()
    annotated_img_path = str(Config.OUTPUTS_DIR / record.annotated_filename)

    pdf_bytes = ReportGenerator.generate_pdf_report(
        analysis_data=data,
        annotated_image_path=annotated_img_path
    )

    pdf_filename = f"CircuitSense_Report_{analysis_id[:8]}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
    )


@app.route("/download/csv/<analysis_id>")
def download_inventory_csv(analysis_id):
    """Exports structured component inventory as CSV."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        abort(404, description="Analysis record not found.")

    data = record.to_dict()
    csv_str = ReportGenerator.generate_inventory_csv(data)
    csv_filename = f"CircuitSense_Inventory_{analysis_id[:8]}.csv"

    return Response(
        csv_str,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
    )


@app.route("/download/json/<analysis_id>")
def download_json_results(analysis_id):
    """Exports complete structured model detections and metrics as JSON."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        abort(404, description="Analysis record not found.")

    return jsonify(record.to_dict())


@app.route("/download/annotated/<analysis_id>")
def download_annotated_image(analysis_id):
    """Downloads the high-resolution annotated circuit board image."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        abort(404, description="Analysis record not found.")

    safe_name = secure_filename(record.annotated_filename)
    return send_from_directory(
        Config.OUTPUTS_DIR,
        safe_name,
        as_attachment=True,
        download_name=f"annotated_{record.original_filename}"
    )


# ============================================================================
# SAFE FILE SERVING ROUTES
# ============================================================================

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    """Safely serves uploaded original images with path traversal protection."""
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400, description="Invalid filename.")
    return send_from_directory(Config.UPLOADS_DIR, safe_name)


@app.route("/outputs/<path:filename>")
def serve_output(filename):
    """Safely serves annotated circuit board images."""
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400, description="Invalid filename.")
    return send_from_directory(Config.OUTPUTS_DIR, safe_name)


@app.route("/crops/<path:filename>")
def serve_crop(filename):
    """Safely serves component bounding box crops."""
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400, description="Invalid filename.")
    return send_from_directory(Config.CROPS_DIR, safe_name)


# ============================================================================
# MANAGEMENT & DELETION ROUTES
# ============================================================================

@app.route("/delete/<analysis_id>", methods=["POST"])
def delete_analysis(analysis_id):
    """Safely removes an analysis record and deletes all associated physical files."""
    record = AnalysisRecord.query.filter_by(analysis_id=analysis_id).first()
    if not record:
        flash(f"Analysis '{analysis_id}' not found.", "error")
        return redirect(url_for("history"))

    try:
        # Delete original uploaded image
        orig_file = Config.UPLOADS_DIR / record.stored_filename
        if orig_file.exists():
            orig_file.unlink()

        # Delete annotated output image
        ann_file = Config.OUTPUTS_DIR / record.annotated_filename
        if ann_file.exists():
            ann_file.unlink()

        # Delete associated component crops
        detections = json.loads(record.detections_json) if record.detections_json else []
        for det in detections:
            crop_name = det.get("crop_filename")
            if crop_name:
                crop_path = Config.CROPS_DIR / crop_name
                if crop_path.exists():
                    crop_path.unlink()

        # Remove database record
        db.session.delete(record)
        db.session.commit()
        flash(f"Analysis '{record.original_filename}' and all associated files were deleted successfully.", "success")
    except Exception as e:
        logger.error(f"Error during deletion of analysis {analysis_id}: {e}")
        db.session.rollback()
        flash(f"Failed to delete analysis: {str(e)}", "error")

    return redirect(url_for("history"))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Custom 404 page."""
    return render_template("errors/404.html", error=error), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error page."""
    db.session.rollback()
    logger.error(f"Internal server error: {error}")
    return render_template("errors/500.html", error=error), 500


@app.errorhandler(RequestEntityTooLarge)
def upload_too_large(error):
    """Custom 413 error handler for oversized files."""
    max_mb = Config.MAX_CONTENT_LENGTH // (1024 * 1024)
    flash(f"File exceeds the maximum allowed upload limit of {max_mb} MB.", "error")
    return redirect(url_for("analyze")), 413


if __name__ == "__main__":
    import socket
    default_port = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _s:
        if _s.connect_ex(("127.0.0.1", default_port)) == 0:
            default_port = 5001
    port = int(os.environ.get("PORT", default_port))
    app.run(host="127.0.0.1", port=port, debug=Config.DEBUG)
