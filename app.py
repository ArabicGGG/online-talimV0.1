import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import desc, func
import mimetypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///online_learning.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Kirish uchun tizimga kiring'

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import models after app initialization
with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    from models import Course, User
    featured_courses = Course.query.filter_by(is_featured=True).limit(6).all()
    recent_courses = Course.query.order_by(desc(Course.created_at)).limit(8).all()
    
    # Get courses with student count
    popular_courses = db.session.query(Course, func.count(models.Enrollment.id).label('student_count'))\
        .outerjoin(models.Enrollment)\
        .group_by(Course.id)\
        .order_by(desc('student_count'))\
        .limit(6).all()
    
    stats = {
        'total_courses': Course.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_instructors': User.query.filter_by(role='instructor').count()
    }
    
    return render_template('index.html', 
                         featured_courses=featured_courses,
                         recent_courses=recent_courses,
                         popular_courses=popular_courses,
                         stats=stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        from models import User
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Muvaffaqiyatli kirildi!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Noto\'g\'ri foydalanuvchi nomi yoki parol', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get('role', 'student')
        
        # Validation
        if password != confirm_password:
            flash('Parollar mos kelmadi', 'error')
            return render_template('register.html')
        
        from models import User
        if User.query.filter_by(username=username).first():
            flash('Bu foydalanuvchi nomi allaqachon mavjud', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu email allaqachon ro\'yxatdan o\'tgan', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Ro\'yxatdan o\'tish muvaffaqiyatli!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Tizimdan chiqildi', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Course, Enrollment, User
    
    if current_user.role == 'instructor':
        my_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        total_students = db.session.query(func.count(Enrollment.id))\
            .join(Course)\
            .filter(Course.instructor_id == current_user.id)\
            .scalar() or 0
        
        return render_template('dashboard.html', 
                             my_courses=my_courses,
                             total_students=total_students)
    else:
        enrolled_courses = db.session.query(Course)\
            .join(Enrollment)\
            .filter(Enrollment.user_id == current_user.id)\
            .all()
        
        return render_template('dashboard.html', 
                             enrolled_courses=enrolled_courses)

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'instructor':
        flash('Faqat o\'qituvchilar kurs yarata oladi', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        from models import Course, Lesson
        
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        
        # Handle course image upload
        course_image = None
        if 'course_image' in request.files:
            file = request.files['course_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                course_image = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], course_image))
        
        # Create course
        course = Course(
            title=title,
            description=description,
            price=price,
            category=category,
            instructor_id=current_user.id,
            image_url=course_image
        )
        
        db.session.add(course)
        db.session.flush()  # Get course ID
        
        # Add lessons
        lesson_count = int(request.form.get('lesson_count', 0))
        for i in range(lesson_count):
            lesson_title = request.form.get(f'lesson_title_{i}')
            lesson_content = request.form.get(f'lesson_content_{i}')
            
            if lesson_title and lesson_content:
                # Handle lesson video upload
                video_url = None
                video_file_key = f'lesson_video_{i}'
                if video_file_key in request.files:
                    video_file = request.files[video_file_key]
                    if video_file and video_file.filename and allowed_file(video_file.filename):
                        video_filename = secure_filename(video_file.filename)
                        video_url = f"lesson_{course.id}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_filename}"
                        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_url))
                
                lesson = Lesson(
                    title=lesson_title,
                    content=lesson_content,
                    video_url=video_url,
                    course_id=course.id,
                    order=i + 1
                )
                db.session.add(lesson)
        
        db.session.commit()
        flash('Kurs muvaffaqiyatli yaratildi!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    
    return render_template('create_course.html')

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    from models import Course, Lesson, Comment, Rating, Enrollment
    
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    
    # Check if user is enrolled
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        is_enrolled = enrollment is not None
    
    # Get comments with user info
    comments = db.session.query(Comment, models.User.username)\
        .join(models.User)\
        .filter(Comment.course_id == course_id)\
        .order_by(desc(Comment.created_at))\
        .all()
    
    # Get ratings
    ratings = Rating.query.filter_by(course_id=course_id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    
    # Get enrollment count
    enrollment_count = Enrollment.query.filter_by(course_id=course_id).count()
    
    return render_template('course_detail.html', 
                         course=course,
                         lessons=lessons,
                         is_enrolled=is_enrolled,
                         comments=comments,
                         avg_rating=avg_rating,
                         total_ratings=len(ratings),
                         enrollment_count=enrollment_count)

@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson_detail(lesson_id):
    from models import Lesson, Course, Enrollment
    
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(lesson.course_id)
    
    # Check if user is enrolled or is the instructor
    if current_user.id != course.instructor_id:
        enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        if not enrollment:
            flash('Bu darsni ko\'rish uchun kursga yozilishingiz kerak', 'error')
            return redirect(url_for('course_detail', course_id=course.id))
    
    # Get all lessons for navigation
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
    
    return render_template('lesson_detail.html', 
                         lesson=lesson,
                         course=course,
                         lessons=lessons)

@app.route('/enroll/<int:course_id>')
@login_required
def enroll_course(course_id):
    from models import Course, Enrollment
    
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if existing_enrollment:
        flash('Siz allaqachon bu kursga yozilgansiz', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # For free courses, enroll directly
    if course.price == 0:
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Kursga muvaffaqiyatli yozildingiz!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    else:
        # For paid courses, add to cart
        return redirect(url_for('add_to_cart', course_id=course_id))

@app.route('/add_to_cart/<int:course_id>')
@login_required
def add_to_cart(course_id):
    from models import Course
    
    course = Course.query.get_or_404(course_id)
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if already in cart
    if course_id not in session['cart']:
        session['cart'].append(course_id)
        flash(f'{course.title} savatga qo\'shildi', 'success')
    else:
        flash('Bu kurs allaqachon savatda', 'info')
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/cart')
@login_required
def cart():
    from models import Course
    
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for course_id in session['cart']:
            course = Course.query.get(course_id)
            if course:
                cart_items.append(course)
                total += course.price
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:course_id>')
@login_required
def remove_from_cart(course_id):
    if 'cart' in session and course_id in session['cart']:
        session['cart'].remove(course_id)
        flash('Kurs savatdan olib tashlandi', 'success')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    from models import Course, Enrollment
    
    if 'cart' not in session or not session['cart']:
        flash('Savatchangiz bo\'sh', 'error')
        return redirect(url_for('cart'))
    
    # Process enrollment for all courses in cart
    for course_id in session['cart']:
        existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if not existing_enrollment:
            enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
            db.session.add(enrollment)
    
    db.session.commit()
    
    # Clear cart
    session['cart'] = []
    
    flash('Kurslar muvaffaqiyatli sotib olindi!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_comment/<int:course_id>', methods=['POST'])
@login_required
def add_comment(course_id):
    from models import Comment
    
    content = request.form['content']
    
    if content.strip():
        comment = Comment(
            content=content,
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Izoh qo\'shildi', 'success')
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/add_rating/<int:course_id>', methods=['POST'])
@login_required
def add_rating(course_id):
    from models import Rating
    
    rating_value = int(request.form['rating'])
    
    # Check if user already rated this course
    existing_rating = Rating.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if existing_rating:
        existing_rating.rating = rating_value
        flash('Baho yangilandi', 'success')
    else:
        rating = Rating(
            rating=rating_value,
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(rating)
        flash('Baho qo\'shildi', 'success')
    
    db.session.commit()
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/profile')
@login_required
def profile():
    from models import Course, Enrollment
    
    if current_user.role == 'instructor':
        my_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('profile.html', my_courses=my_courses)
    else:
        enrolled_courses = db.session.query(Course)\
            .join(Enrollment)\
            .filter(Enrollment.user_id == current_user.id)\
            .all()
        return render_template('profile.html', enrolled_courses=enrolled_courses)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/cart/count')
@login_required
def get_cart_count():
    count = len(session.get('cart', []))
    return jsonify({'count': count})

@app.route('/search')
def search():
    from models import Course
    
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    courses_query = Course.query
    
    if query:
        courses_query = courses_query.filter(Course.title.contains(query))
    
    if category:
        courses_query = courses_query.filter_by(category=category)
    
    courses = courses_query.all()
    
    return render_template('search_results.html', 
                         courses=courses, 
                         query=query, 
                         category=category)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
