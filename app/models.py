# app/models.py
# SQLAlchemy models for the Fleet Management application.

from app import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    language_preference = db.Column(db.String(5), nullable=True, default='en')
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())

class Secteur(db.Model):
    __tablename__ = 'secteurs'
    id = db.Column(db.Integer, primary_key=True)
    secteur_name = db.Column(db.String(255), nullable=False, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    description = db.Column(db.Text)

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(50), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    secteur_id = db.Column(db.Integer, db.ForeignKey('secteurs.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())

class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), nullable=False, unique=True)
    imei = db.Column(db.String(15), nullable=False, unique=True)
    serial_number = db.Column(db.String(100), nullable=False, unique=True)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())

class SimCard(db.Model):
    __tablename__ = 'sim_cards'
    id = db.Column(db.Integer, primary_key=True)
    iccid = db.Column(db.String(22), nullable=False, unique=True)
    carrier = db.Column(db.String(100))
    plan_details = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)

class PhoneNumber(db.Model):
    __tablename__ = 'phone_numbers'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    sim_card_id = db.Column(db.Integer, db.ForeignKey('sim_cards.id'), unique=True)
    status = db.Column(db.String(20), nullable=False)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)
    sim_card_id = db.Column(db.Integer, db.ForeignKey('sim_cards.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    assignment_date = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    return_date = db.Column(db.DateTime(timezone=True), nullable=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)
    reported_by_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_support_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)

class TicketUpdate(db.Model):
    __tablename__ = 'ticket_updates'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    update_author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    is_internal_note = db.Column(db.Boolean, nullable=False, default=False)

class AssetHistoryLog(db.Model):
    __tablename__ = 'asset_history_log'
    id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(20), nullable=False)
    asset_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    details = db.Column(db.Text)
