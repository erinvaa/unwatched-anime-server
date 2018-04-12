from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

db = SQLAlchemy()

guild_members_association = db.Table('guild_members', db.Model.metadata,
                                     db.Column('guild_id', db.Integer, db.ForeignKey('guilds.id')),
                                     db.Column('player_id', db.Integer, db.ForeignKey('players.id')))

held_items_association = db.Table('held_items', db.Model.metadata,
                                  db.Column('player_id', db.Integer, db.ForeignKey('players.id')),
                                  db.Column('item_id', db.Integer, db.ForeignKey('items.id')))


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String, nullable=False)
    email_address = db.Column(db.String, unique=True, nullable=False)
    skill_points = db.Column(db.Integer, nullable=False)
    items = db.relationship("Item", secondary=held_items_association)


class Guild(db.Model):
    __tablename__ = 'guilds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String(10))
    members = db.relationship("Player", secondary=guild_members_association, backref="guilds")


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    skill_points_modifier = db.Column(db.Integer, nullable=False)
