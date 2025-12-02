import os
from PIL import Image
from flask import (Flask, render_template, request, redirect, url_for, flash,
                   send_from_directory, session)
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config
from models import db, Member, Event, Announcement, GalleryImage, ContactMessage
from forms import ContactForm, EventForm, AnnouncementForm, GalleryForm, MemberForm, AdminLoginForm

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

ALLOWED = app.config['ALLOWED_MEDIA_EXTENSIONS']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

# Public routes
@app.route('/')
def index():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()
    upcoming = Event.query.filter(Event.date >= datetime.utcnow().date()).order_by(Event.date).limit(5).all()
    return render_template('index.html', announcements=announcements, upcoming=upcoming)

@app.route('/about')
def about():
    members = Member.query.order_by(Member.joined_at.desc()).all()
    return render_template('about.html', members=members)

@app.route('/events')
def events():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('events.html', events=events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

# ---------------------------
# PUBLIC GALLERY ROUTES (FIXED)
# ---------------------------

# Show list of albums
@app.route('/gallery')
def gallery_albums():
    categories = db.session.query(GalleryImage.category).distinct().all()

    albums = {}
    for c in categories:
        cat = c[0] or "uncategorized"
        count = GalleryImage.query.filter_by(category=cat).count()

        # Use the latest uploaded image in the category as the album cover
        cover_img = GalleryImage.query.filter_by(category=cat).order_by(GalleryImage.uploaded_at.desc()).first()
        cover_filename = cover_img.filename if cover_img else None

        albums[cat] = {
            'count': count,
            'cover': cover_filename
        }

    return render_template("gallery_albums.html", albums=albums)


# Show images from one album
@app.route('/gallery/<string:category>')
def gallery_category(category):
    images = GalleryImage.query.filter_by(category=category).all()
    return render_template("gallery_view.html", category=category, images=images)

@app.route('/announcements')
def announcements():
    notes = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html', notes=notes)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Message sent. Thank you!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#----------------------
#ADMIN ROUTES
#---------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.password.data == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Welcome, admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Wrong password', 'danger')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin login required', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_members = Member.query.count()
    total_events = Event.query.count()
    total_images = GalleryImage.query.count()
    total_messages = ContactMessage.query.count()
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('admin/dashboard.html', total_members=total_members,
                           total_events=total_events, total_images=total_images,
                           total_messages=total_messages, events=events)

# Admin events
@app.route('/admin/events')
@admin_required
def admin_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin/events.html', events=events)

@app.route('/admin/events/add', methods=['GET', 'POST'])
@admin_required
def admin_add_event():
    form = EventForm()
    if form.validate_on_submit():
        filename = None
        f = request.files.get('poster')
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{ts}_{fname}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        event = Event(title=form.title.data, description=form.description.data,
                      date=form.date.data, time=form.time.data, poster=filename)
        db.session.add(event)
        db.session.commit()
        flash('Event added', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/event_form.html', form=form)

@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        f = request.files.get('poster')
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{ts}_{fname}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            event.poster = filename
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.time = form.time.data
        db.session.commit()
        flash('Event updated', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/event_form.html', form=form, event=event)

@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.poster:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], event.poster))
        except Exception:
            pass
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted', 'info')
    return redirect(url_for('admin_events'))

# Admin gallery# Admin gallery
@app.route('/admin/gallery', methods=['GET', 'POST'])
@admin_required
def admin_gallery():
    form = GalleryForm()

    if request.method == "POST":
        # Support both multiple-file input named "images" and single-file WTForms field "image"
        files = request.files.getlist("images")  # MULTIPLE FILES

        # If the template uses the WTForms single FileField (name="image"), fall back to that
        if not files or files == [""]:
            single = request.files.get('image')
            files = [single] if single else []

        # Filter out empty or unnamed file entries
        files = [f for f in files if f and getattr(f, 'filename', None)]

        if not files:
            flash("No files selected", "danger")
            return redirect(url_for('admin_gallery'))

        for f in files:
            if f and allowed_file(f.filename):
                fname = secure_filename(f.filename)

                # Add timestamp for unique filename
                ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                filename = f"{ts}_{fname}"

                # Save file
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Save DB entry with category
                img = GalleryImage(
                    filename=filename,
                    caption=form.caption.data,
                    category=form.category.data     # ✅ STORE CATEGORY
                )
                db.session.add(img)
            else:
                flash(f"Invalid file: {getattr(f, 'filename', 'Unknown')}", "danger")

        db.session.commit()
        flash("Files uploaded successfully!", "success")
        return redirect(url_for('admin_gallery'))

    # Display all images/videos
    images = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()

    return render_template('admin/gallery.html', images=images, form=form)


@app.route('/admin/gallery/<int:image_id>/delete', methods=['POST'])
@admin_required
def admin_delete_image(image_id):
    img = GalleryImage.query.get_or_404(image_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
    except Exception:
        pass
    db.session.delete(img)
    db.session.commit()
    flash('Image deleted', 'info')
    return redirect(url_for('admin_gallery'))

# Admin members
@app.route('/admin/members', methods=['GET', 'POST'])
@admin_required
def admin_members():
    form = MemberForm()
    if form.validate_on_submit():
        filename = None
        f = request.files.get('photo')
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{ts}_{fname}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        member = Member(name=form.name.data, role=form.role.data, bio=form.bio.data, photo=filename)
        db.session.add(member)
        db.session.commit()
        flash('Member added', 'success')
        return redirect(url_for('admin_members'))
    members = Member.query.order_by(Member.joined_at.desc()).all()
    return render_template('admin/members.html', members=members, form=form)

@app.route('/admin/members/<int:member_id>/delete', methods=['POST'])
@admin_required
def admin_delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    if member.photo:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], member.photo))
        except Exception:
            pass
    db.session.delete(member)
    db.session.commit()
    flash('Member removed', 'info')
    return redirect(url_for('admin_members'))

# Admin announcements
@app.route('/admin/announcements', methods=['GET', 'POST'])
@admin_required
def admin_announcements():
    form = AnnouncementForm()
    if form.validate_on_submit():
        note = Announcement(title=form.title.data, content=form.content.data)
        db.session.add(note)
        db.session.commit()
        flash('Announcement published', 'success')
        return redirect(url_for('admin_announcements'))
    notes = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', notes=notes, form=form)

@app.route('/admin/contacts')
@admin_required
def admin_contacts():
    contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)


if __name__ == '__main__':
    app.run(debug=True)
