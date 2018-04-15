from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    short_code = db.Column(db.String, nullable=True)


class VideoSourceType(db.Model):
    __tablename__ = 'video_source_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    icon_url = db.Column(db.String, nullable=True)
    domain = db.Column(db.String, nullable=True)
    sources = db.relationship('VideoSource', backref='type', lazy=True)
    custom_sources = db.relationship('CustomVideoSource', backref='type', lazy=True)


class VideoSource(db.Model):
    __tablename__ = 'video_source'

    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    video_source_type = db.Column(db.Integer, db.ForeignKey('video_source_types.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)


class CustomVideoSource(db.Model):
    __tablename__ = 'custom_video_source'

    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_source_type = db.Column(db.Integer, db.ForeignKey('video_source_types.id'), nullable=True)


class SkippedEpisodes(db.Model):
    __tablename__ = 'skipped_episodes'

    mal_id = db.Column(db.Integer, primary_key=True)
    skipped_episodes = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    mal_name = db.Column(db.String, nullable=False)
    default_country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=True)
    custom_video_sources = db.relationship('CustomVideoSource', backref='user', lazy=True)



