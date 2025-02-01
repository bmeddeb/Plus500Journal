# models.py

from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy db instance.
db = SQLAlchemy()


class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    trade_date = db.Column(db.String, nullable=False)  # Stored in ISO8601 format (e.g., "2025-01-31 12:53:00")
    action = db.Column(db.String, nullable=False)  # "Buy" or "Sell"
    amount = db.Column(db.Integer, nullable=False)  # Number of contracts traded
    instrument = db.Column(db.String, nullable=False)  # Instrument name (e.g., "Micro E-mini Nasdaq-100 Mar 25")
    average_open_price = db.Column(db.Float, nullable=False)  # Average open price
    close_price = db.Column(db.Float, nullable=False)  # Close price
    gross_pl = db.Column(db.Float, nullable=False)  # Gross profit/loss
    net_pl = db.Column(db.Float, nullable=False)  # Net profit/loss (after fees, etc.)
    close_trade_id = db.Column(db.Integer, nullable=False)  # Trade identifier
