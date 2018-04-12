from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
    video_source_type = db.Column(db.Integer, db.ForeignKey('video_source_types.id'), nullable=False)

