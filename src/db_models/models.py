import datetime

from dbs.db import db, metadata


class User(db.Model):
    __tablename__ = 'users'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    login = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<User {self.login}>'


class JwtRefresh(db.Model):
    __tablename__ = 'jwt'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    refresh_token = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<JWT refresh token for user {self.user_id}>'


class Login(db.Model):
    __tablename__ = 'logins'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    info = db.Column(db.String)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Login user {self.user_id}>'


class MetricUser(db.Model):
    __tablename__ = 'metric_users'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<MetricUser {self.id}>'


class Metric(db.Model):
    __tablename__ = 'metrics'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('metric_users.id', ondelete='CASCADE'), nullable=False)
    metric_name = db.Column(db.String, nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'metric_name', name='metric_pk'),)

    def __repr__(self):
        return f'<Med metrics user {self.user_id}>'


class MetricData(db.Model):
    __tablename__ = 'metric_data'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    metric_id = db.Column(db.Integer, db.ForeignKey('metrics.id', ondelete='CASCADE'), nullable=False)
    metric_date = db.Column(db.Date, nullable=False)
    metric_value = db.Column(db.Float)
    __table_args__ = (db.UniqueConstraint('metric_id', 'metric_date', name='metric_data_pk'),)

    def __repr__(self):
        return f'<Metric data {self.id}-{self.metric_date}>'


class MetricResult(db.Model):
    __tablename__ = 'metric_results'
    metadata = metadata
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('metric_users.id', ondelete='CASCADE'), nullable=False)
    metric_first = db.Column(db.Integer, db.ForeignKey('metrics.id', ondelete='CASCADE'), nullable=False)
    metric_second = db.Column(db.Integer, db.ForeignKey('metrics.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Float)
    p_value = db.Column(db.Float)
    __table_args__ = (db.UniqueConstraint('user_id', 'metric_first', 'metric_second', name='metric_result_pk'),)

    def __repr__(self):
        return f'<Med results {self.user_id}>: {self.metric_first}+{self.metric_second}'
