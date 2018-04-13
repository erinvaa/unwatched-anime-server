from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class VideoSourceType(db.Model):
    __tablename__ = 'video_source_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    icon_url = db.Column(db.String, nullable=True)
    sources = db.relationship('VideoSource', backref='type', lazy=True)


class VideoSource(db.Model):
    __tablename__ = 'video_source'

    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)
    video_source_type = db.Column(db.Integer, db.ForeignKey('video_source_types.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)


class SkippedEpisodes(db.Model):
    __tablename__ = 'skipped_episodes'

    mal_id = db.Column(db.Integer, primary_key=True)
    skipped_episodes = db.Column(db.Integer, nullable=False)
