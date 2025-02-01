# app.py
import calendar
import csv
import io
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Trade
from Dashboard import init_dashboard


def create_app():
    app = Flask(__name__)

    # Configure the SQLite database and a secret key for flash messages
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'

    # Initialize the SQLAlchemy database with the Flask app
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        # Query all trades from the database
        trades = Trade.query.all()

        # Group trades by day (using the "YYYY-MM-DD" part of trade_date)
        daily_pl = {}
        for trade in trades:
            # trade.trade_date is stored as "YYYY-MM-DD HH:MM:SS"
            day = trade.trade_date.split(" ")[0]  # extract the date part
            daily_pl.setdefault(day, 0)
            daily_pl[day] += trade.net_pl

        # Determine which month and year to display (default to current month)
        today = date.today()
        year = request.args.get("year", today.year, type=int)
        month = request.args.get("month", today.month, type=int)

        # Generate the calendar grid for the specified month.
        cal = calendar.Calendar(firstweekday=6)  # starting with Sunday
        month_days = cal.monthdayscalendar(year, month)

        # Compute total monthly profit/loss from our daily_pl dictionary.
        total_month_pl = sum(
            pl for day_str, pl in daily_pl.items() if day_str.startswith(f"{year}-{month:02d}")
        )

        return render_template(
            'index.html',
            year=year,
            month=month,
            month_days=month_days,
            daily_pl=daily_pl,
            total_month_pl=total_month_pl
        )

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part in the request.')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No file selected.')
                return redirect(request.url)
            if file and file.filename.lower().endswith('.csv'):
                data = file.stream.read().decode("UTF8")
                stream = io.StringIO(data)
                try:
                    dialect = csv.Sniffer().sniff(data)
                except csv.Error:
                    dialect = csv.get_dialect('excel')
                csv_input = csv.DictReader(stream, dialect=dialect)
                count = 0
                for row in csv_input:
                    try:
                        date_str = row['Date'].strip()
                        try:
                            if 'AM' in date_str.upper() or 'PM' in date_str.upper():
                                date_obj = datetime.strptime(date_str, "%m/%d/%Y %I:%M %p")
                            else:
                                date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
                        except ValueError:
                            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                            date_obj = date_obj.replace(hour=0, minute=0, second=0)
                        iso_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

                        # Helper function to clean numeric strings (remove "$", commas, etc.)
                        def clean_number(num_str):
                            num_str = num_str.replace('$', '').replace(',', '').strip()
                            if num_str.startswith('(') and num_str.endswith(')'):
                                num_str = '-' + num_str[1:-1]
                            return float(num_str)

                        amount = int(row['Amount'])
                        average_open_price = clean_number(row['AverageOpenPrice'])
                        close_price = clean_number(row['ClosePrice'])
                        gross_pl = clean_number(row['GrossPl'])
                        net_pl = clean_number(row['NetPl'])
                        close_trade_id = int(row['CloseTradeId'])

                        trade = Trade(
                            trade_date=iso_date,
                            action=row['Action'],
                            amount=amount,
                            instrument=row['Instrument'],
                            average_open_price=average_open_price,
                            close_price=close_price,
                            gross_pl=gross_pl,
                            net_pl=net_pl,
                            close_trade_id=close_trade_id
                        )
                        db.session.add(trade)
                        count += 1
                    except Exception as e:
                        print("Error processing row:", row, e)
                db.session.commit()
                flash(f'Successfully imported {count} trades.')
                return redirect(url_for('index'))
            else:
                flash('Invalid file format. Please upload a CSV file.')
                return redirect(request.url)
        return render_template('upload.html')

    return app


if __name__ == '__main__':
    app = create_app()
    dash_app = init_dashboard(app)
    app.run(debug=True)
