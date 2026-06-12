from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def settings_page():
    # Load current app settings
    config_dict = {
        "SLM_PROVIDER": current_app.config.get("SLM_PROVIDER", "mock"),
        "OLLAMA_URL": current_app.config.get("OLLAMA_URL", ""),
        "OLLAMA_MODEL": current_app.config.get("OLLAMA_MODEL", ""),
        "HF_MODEL_PATH": current_app.config.get("HF_MODEL_PATH", "")
    }
    
    return render_template(
        'settings.html',
        config=config_dict,
        active_page='settings'
    )

@settings_bp.route('/settings/update', methods=['POST'])
def update_settings():
    provider = request.form.get('slm_provider')
    ollama_url = request.form.get('ollama_url')
    ollama_model = request.form.get('ollama_model')
    hf_path = request.form.get('hf_model_path')
    
    if provider not in ['mock', 'ollama', 'huggingface']:
        flash("Invalid SLM provider selected.", "error")
        return redirect(url_for('settings.settings_page'))
        
    try:
        # Update configurations in-memory
        current_app.config["SLM_PROVIDER"] = provider
        current_app.config["OLLAMA_URL"] = ollama_url
        current_app.config["OLLAMA_MODEL"] = ollama_model
        current_app.config["HF_MODEL_PATH"] = hf_path
        
        flash("System settings updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating settings: {e}", "error")
        
    return redirect(url_for('settings.settings_page'))
