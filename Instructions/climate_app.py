import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
# Import engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using data as the key"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert list of tuples into normal list
    all_prcps = list(np.ravel(results))

    return jsonify(all_prcps)


@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations from the dataset"""
    # Query all passengers
    results = session.query(Station.station).all()

    return jsonify(results)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    lines = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    for line in lines:
        last_date = line.date

    # Calculate the date 1 year ago from the last data point in the database

        # Convert last date to datetime object
    cutoff_date = dt.date.fromisoformat(last_date) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and temperature
    temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= cutoff_date).order_by(Measurement.date).all()

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start(start):
    lines = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    for line in lines:
        last_date = line.date
    temps = calc_temps(start, last_date)
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    temps = calc_temps(start, end)
    return jsonify(temps)

# Function to calc temperatures
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

if __name__ == '__main__':
    app.run(debug=True)
