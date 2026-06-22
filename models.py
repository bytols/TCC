from extensions import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, DateTime
from datetime import datetime


class Session(db.Model):
    __tablename__ = "session"
    id = Column(Integer, primary_key=True)
    state = Column(String(20), nullable=False, default="LOBBY")
    started_at = Column(DateTime, default=datetime.utcnow)
    # Round whose votes are shown on the FINAL screen. Set to the round where a
    # match (consensus) was reached, or 3 when the game runs its full course.
    result_round = Column(Integer, nullable=True)
    # Seconds from game start until consensus was reached (frozen at FINAL).
    result_seconds = Column(Integer, nullable=True)
    # Timestamp when the most recent ROUND_X started (used by Slice 4 LED timer).
    round_started_at = Column(DateTime, nullable=True)

    players = db.relationship("Player", backref="session", lazy=True)


class Player(db.Model):
    __tablename__ = "player"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    character_json = Column(Text, nullable=False, default="{}")
    avatar_path = Column(String(200), nullable=True)
    session_id = Column(Integer, ForeignKey("session.id"), nullable=False)

    votes = db.relationship("Vote", backref="player", lazy=True)


class Vote(db.Model):
    __tablename__ = "vote"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    movie_id = Column(String(100), nullable=False)
    movie_title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)

    __table_args__ = (UniqueConstraint("player_id", "round_number", "movie_id"),)


class RoundPool(db.Model):
    __tablename__ = "round_pool"
    id = Column(Integer, primary_key=True)
    round_number = Column(Integer, nullable=False)
    movie_id = Column(String(100), nullable=False)
    movie_title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)


def create_tables():
    db.create_all()


def clear_all():
    db.drop_all()
    db.create_all()
