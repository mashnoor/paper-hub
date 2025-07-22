import os
import uuid
from flask import render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app.main import main_bp
from app.models import db, Paper, Category
from app.main.utils import allowed_file, extract_text_from_pdf, extract_metadata_openrouter


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    papers = Paper.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('main/dashboard.html', papers=papers, categories=categories)


@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        category_id = request.form.get('category_id')
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            ext = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(filepath)
            
            # Extract metadata
            metadata = extract_metadata_openrouter(
                pdf_text, 
                current_app.config.get('OPENROUTER_API_KEY')
            )
            
            # Create paper record
            paper = Paper(
                title=metadata['title'],
                authors=metadata['authors'],
                abstract=metadata['abstract'],
                filename=filename,
                user_id=current_user.id,
                category_id=category_id if category_id else None
            )
            db.session.add(paper)
            db.session.commit()
            
            flash('Paper uploaded successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid file type. Only PDF files are allowed.', 'error')
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('main/upload.html', categories=categories)


@main_bp.route('/category/create', methods=['POST'])
@login_required
def create_category():
    name = request.form.get('name')
    color = request.form.get('color', '#007bff')
    
    if name:
        category = Category(name=name, color=color, user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
    
    return redirect(url_for('main.dashboard'))


@main_bp.route('/paper/<int:paper_id>')
@login_required
def view_paper(paper_id):
    paper = Paper.query.filter_by(id=paper_id, user_id=current_user.id).first_or_404()
    # Print the paper filename for debugging/logging
    print(f"Viewing paper: {paper.filename}")
    print(f"Upload folder: {current_app.config['UPLOAD_FOLDER']}")
    print(f"Full path: {os.path.join(current_app.config['UPLOAD_FOLDER'], paper.filename)}")

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], paper.filename)


@main_bp.route('/paper/<int:paper_id>/delete', methods=['POST'])
@login_required
def delete_paper(paper_id):
    paper = Paper.query.filter_by(id=paper_id, user_id=current_user.id).first_or_404()
    
    # Delete file
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], paper.filename))
    except:
        pass
    
    db.session.delete(paper)
    db.session.commit()
    flash('Paper deleted successfully!', 'success')
    return redirect(url_for('main.dashboard')) 