"""
環境保全型農業直接支払交付金 管理システム
自治体職員向け申請管理・審査・交付金算定Webアプリケーション
"""

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///kankyohosen.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─────────────────────────────────────────
# 定数：取組区分と単価（円/10a）
# ─────────────────────────────────────────
ACTIVITY_TYPES = {
    'organic':         {'label': '有機農業',          'unit_price': 12000},
    'cover_crop':      {'label': 'カバークロップ',      'unit_price':  6000},
    'compost':         {'label': '堆肥の施用',          'unit_price':  4400},
    'living_mulch':    {'label': 'リビングマルチ',      'unit_price':  6000},
    'grass_cult':      {'label': '草生栽培',            'unit_price':  6000},
    'no_till':         {'label': '不耕起播種',          'unit_price':  6000},
    'autumn_till':     {'label': '秋耕',               'unit_price':  3000},
    'winter_flood':    {'label': '冬期湛水管理',        'unit_price':  8000},
    'mid_drainage':    {'label': '長期中干し',          'unit_price':  3000},
}

APPLICATION_STATUSES = {
    'draft':    '下書き',
    'submitted':'申請受付',
    'review':   '審査中',
    'approved': '承認済',
    'rejected': '却下',
    'paid':     '交付済',
}


# ─────────────────────────────────────────
# モデル定義
# ─────────────────────────────────────────

class Applicant(db.Model):
    """申請者（農業者）"""
    __tablename__ = 'applicants'

    id = db.Column(db.Integer, primary_key=True)
    farmer_code = db.Column(db.String(20), unique=True, nullable=False)  # 農業者コード
    name = db.Column(db.String(100), nullable=False)
    name_kana = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(8), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship('Application', back_populates='applicant', lazy='dynamic')

    def __repr__(self):
        return f'<Applicant {self.farmer_code} {self.name}>'


class Application(db.Model):
    """交付金申請"""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(20), unique=True, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicants.id'), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)  # 交付年度
    status = db.Column(db.String(20), nullable=False, default='submitted')
    total_amount = db.Column(db.Integer, default=0)  # 交付金合計（円）
    note = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewer_name = db.Column(db.String(50))
    approved_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = db.relationship('Applicant', back_populates='applications')
    activities = db.relationship('Activity', back_populates='application', cascade='all, delete-orphan')

    def calculate_total(self):
        """交付金合計を算出して更新"""
        total = sum(a.subsidy_amount for a in self.activities)
        self.total_amount = total
        return total

    def status_label(self):
        return APPLICATION_STATUSES.get(self.status, self.status)

    def __repr__(self):
        return f'<Application {self.application_number}>'


class Activity(db.Model):
    """取組内容（申請に紐づく農業取組）"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    activity_type = db.Column(db.String(30), nullable=False)  # ACTIVITY_TYPES のキー
    field_name = db.Column(db.String(100))      # 圃場名
    area_a = db.Column(db.Numeric(10, 2), nullable=False)  # 面積（a：アール）
    subsidy_amount = db.Column(db.Integer, default=0)       # 交付金額（円）

    application = db.relationship('Application', back_populates='activities')

    @property
    def area_tan(self):
        """面積をtan（10a）単位に変換"""
        return float(self.area_a) / 10.0

    @property
    def activity_label(self):
        return ACTIVITY_TYPES.get(self.activity_type, {}).get('label', self.activity_type)

    @property
    def unit_price(self):
        return ACTIVITY_TYPES.get(self.activity_type, {}).get('unit_price', 0)

    def calculate_amount(self):
        """交付金額 = 単価(円/10a) × 面積(a) / 10"""
        price = ACTIVITY_TYPES.get(self.activity_type, {}).get('unit_price', 0)
        self.subsidy_amount = int(price * float(self.area_a) / 10.0)
        return self.subsidy_amount


def generate_application_number(year):
    """申請番号を採番: YYYY-XXXXXX"""
    last = (Application.query
            .filter_by(fiscal_year=year)
            .order_by(Application.id.desc())
            .first())
    seq = (last.id + 1) if last else 1
    count = Application.query.filter_by(fiscal_year=year).count() + 1
    return f'{year}-{count:06d}'


def generate_farmer_code():
    """農業者コードを採番"""
    last = Applicant.query.order_by(Applicant.id.desc()).first()
    seq = (last.id + 1) if last else 1
    return f'F{seq:07d}'


# ─────────────────────────────────────────
# ルーティング
# ─────────────────────────────────────────

@app.route('/')
def index():
    """ダッシュボード"""
    current_year = date.today().year
    stats = {
        'total_applicants': Applicant.query.count(),
        'total_applications': Application.query.count(),
        'submitted': Application.query.filter_by(status='submitted').count(),
        'review': Application.query.filter_by(status='review').count(),
        'approved': Application.query.filter_by(status='approved').count(),
        'paid': Application.query.filter_by(status='paid').count(),
        'current_year': current_year,
        'year_total': (db.session.query(db.func.sum(Application.total_amount))
                       .filter_by(fiscal_year=current_year).scalar() or 0),
    }
    recent = (Application.query
              .order_by(Application.created_at.desc())
              .limit(10).all())
    return render_template('index.html', stats=stats, recent=recent,
                           statuses=APPLICATION_STATUSES)


# ── 申請者管理 ──────────────────────────────

@app.route('/applicants')
def applicant_list():
    q = request.args.get('q', '').strip()
    query = Applicant.query
    if q:
        query = query.filter(
            db.or_(Applicant.name.contains(q),
                   Applicant.name_kana.contains(q),
                   Applicant.farmer_code.contains(q))
        )
    applicants = query.order_by(Applicant.id.desc()).all()
    return render_template('applicant_list.html', applicants=applicants, q=q)


@app.route('/applicants/new', methods=['GET', 'POST'])
def applicant_new():
    if request.method == 'POST':
        applicant = Applicant(
            farmer_code=generate_farmer_code(),
            name=request.form['name'].strip(),
            name_kana=request.form['name_kana'].strip(),
            postal_code=request.form['postal_code'].strip(),
            address=request.form['address'].strip(),
            phone=request.form['phone'].strip(),
        )
        db.session.add(applicant)
        db.session.commit()
        flash(f'申請者「{applicant.name}」を登録しました。', 'success')
        return redirect(url_for('applicant_detail', id=applicant.id))
    return render_template('applicant_form.html', applicant=None)


@app.route('/applicants/<int:id>')
def applicant_detail(id):
    applicant = Applicant.query.get_or_404(id)
    applications = (applicant.applications
                    .order_by(Application.fiscal_year.desc()).all())
    return render_template('applicant_detail.html',
                           applicant=applicant, applications=applications,
                           statuses=APPLICATION_STATUSES)


@app.route('/applicants/<int:id>/edit', methods=['GET', 'POST'])
def applicant_edit(id):
    applicant = Applicant.query.get_or_404(id)
    if request.method == 'POST':
        applicant.name = request.form['name'].strip()
        applicant.name_kana = request.form['name_kana'].strip()
        applicant.postal_code = request.form['postal_code'].strip()
        applicant.address = request.form['address'].strip()
        applicant.phone = request.form['phone'].strip()
        applicant.updated_at = datetime.utcnow()
        db.session.commit()
        flash('申請者情報を更新しました。', 'success')
        return redirect(url_for('applicant_detail', id=applicant.id))
    return render_template('applicant_form.html', applicant=applicant)


# ── 申請管理 ──────────────────────────────

@app.route('/applications')
def application_list():
    status = request.args.get('status', '')
    year = request.args.get('year', '', type=str)
    q = request.args.get('q', '').strip()

    query = Application.query.join(Applicant)
    if status:
        query = query.filter(Application.status == status)
    if year:
        query = query.filter(Application.fiscal_year == int(year))
    if q:
        query = query.filter(
            db.or_(Application.application_number.contains(q),
                   Applicant.name.contains(q),
                   Applicant.farmer_code.contains(q))
        )
    applications = query.order_by(Application.id.desc()).all()
    years = (db.session.query(Application.fiscal_year)
             .distinct().order_by(Application.fiscal_year.desc()).all())
    years = [y[0] for y in years]
    return render_template('application_list.html',
                           applications=applications,
                           statuses=APPLICATION_STATUSES,
                           years=years,
                           current_status=status,
                           current_year=year,
                           q=q)


@app.route('/applications/new', methods=['GET', 'POST'])
def application_new():
    applicant_id = request.args.get('applicant_id', type=int)
    applicant = Applicant.query.get(applicant_id) if applicant_id else None

    if request.method == 'POST':
        applicant_id = int(request.form['applicant_id'])
        applicant = Applicant.query.get_or_404(applicant_id)
        fiscal_year = int(request.form['fiscal_year'])

        app_obj = Application(
            application_number=generate_application_number(fiscal_year),
            applicant_id=applicant_id,
            fiscal_year=fiscal_year,
            status='submitted',
            note=request.form.get('note', ''),
        )
        db.session.add(app_obj)
        db.session.flush()  # IDを確定させる

        # 取組情報を登録
        activity_types = request.form.getlist('activity_type[]')
        field_names = request.form.getlist('field_name[]')
        areas = request.form.getlist('area_a[]')

        for act_type, field, area in zip(activity_types, field_names, areas):
            if act_type and area:
                activity = Activity(
                    application_id=app_obj.id,
                    activity_type=act_type,
                    field_name=field.strip(),
                    area_a=Decimal(area),
                )
                activity.calculate_amount()
                db.session.add(activity)

        app_obj.calculate_total()
        db.session.commit()
        flash(f'申請番号 {app_obj.application_number} を受け付けました。', 'success')
        return redirect(url_for('application_detail', id=app_obj.id))

    current_year = date.today().year
    applicants = Applicant.query.order_by(Applicant.name).all()
    return render_template('application_form.html',
                           applicant=applicant,
                           applicants=applicants,
                           activity_types=ACTIVITY_TYPES,
                           current_year=current_year)


@app.route('/applications/<int:id>')
def application_detail(id):
    app_obj = Application.query.get_or_404(id)
    return render_template('application_detail.html',
                           app=app_obj,
                           activity_types=ACTIVITY_TYPES,
                           statuses=APPLICATION_STATUSES)


@app.route('/applications/<int:id>/status', methods=['POST'])
def application_update_status(id):
    app_obj = Application.query.get_or_404(id)
    new_status = request.form['status']
    reviewer = request.form.get('reviewer_name', '').strip()

    if new_status not in APPLICATION_STATUSES:
        abort(400)

    app_obj.status = new_status
    now = datetime.utcnow()

    if new_status == 'review':
        app_obj.reviewed_at = now
        app_obj.reviewer_name = reviewer
    elif new_status == 'approved':
        app_obj.approved_at = now
        if reviewer:
            app_obj.reviewer_name = reviewer
    elif new_status == 'paid':
        app_obj.paid_at = now

    app_obj.updated_at = now
    db.session.commit()
    flash(f'申請のステータスを「{APPLICATION_STATUSES[new_status]}」に更新しました。', 'success')
    return redirect(url_for('application_detail', id=id))


@app.route('/applications/<int:id>/recalculate', methods=['POST'])
def application_recalculate(id):
    app_obj = Application.query.get_or_404(id)
    for activity in app_obj.activities:
        activity.calculate_amount()
    app_obj.calculate_total()
    db.session.commit()
    flash('交付金額を再計算しました。', 'info')
    return redirect(url_for('application_detail', id=id))


# ── 集計レポート ──────────────────────────────

@app.route('/reports')
def reports():
    years = (db.session.query(Application.fiscal_year)
             .distinct().order_by(Application.fiscal_year.desc()).all())
    years = [y[0] for y in years]
    selected_year = request.args.get('year', date.today().year, type=int)

    # 年度別集計
    year_apps = Application.query.filter_by(fiscal_year=selected_year).all()
    total_amount = sum(a.total_amount for a in year_apps)
    paid_amount = sum(a.total_amount for a in year_apps if a.status == 'paid')

    # 取組区分別集計
    activity_summary = {}
    for key, info in ACTIVITY_TYPES.items():
        acts = (Activity.query
                .join(Application)
                .filter(Application.fiscal_year == selected_year)
                .filter(Activity.activity_type == key)
                .all())
        if acts:
            activity_summary[key] = {
                'label': info['label'],
                'count': len(acts),
                'total_area': sum(float(a.area_a) for a in acts),
                'total_amount': sum(a.subsidy_amount for a in acts),
            }

    status_summary = {}
    for status_key, status_label in APPLICATION_STATUSES.items():
        count = Application.query.filter_by(
            fiscal_year=selected_year, status=status_key).count()
        if count:
            status_summary[status_key] = {'label': status_label, 'count': count}

    return render_template('reports.html',
                           years=years,
                           selected_year=selected_year,
                           year_apps=year_apps,
                           total_amount=total_amount,
                           paid_amount=paid_amount,
                           activity_summary=activity_summary,
                           status_summary=status_summary)


# ─────────────────────────────────────────
# テンプレートフィルター
# ─────────────────────────────────────────

@app.template_filter('jpy')
def jpy_filter(value):
    """金額を日本円形式で表示"""
    return f'¥{int(value):,}'

@app.template_filter('datetime_jp')
def datetime_jp_filter(value):
    if value is None:
        return '—'
    return value.strftime('%Y年%m月%d日 %H:%M')

@app.template_filter('date_jp')
def date_jp_filter(value):
    if value is None:
        return '—'
    return value.strftime('%Y年%m月%d日')


# ─────────────────────────────────────────
# 起動
# ─────────────────────────────────────────

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
