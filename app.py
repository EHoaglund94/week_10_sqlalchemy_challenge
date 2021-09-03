#imports
import numpy
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

######################################################################
#Database Setup
######################################################################
engine = create_engine("sqlite:///hawaii.sqlite")
#reflect an existing database into a new model
Base = automap_base()
#rflect the tables
Base.prepare(engine, reflect = True)

#save references to table
measurement = Base.classes.measurement
station = Base.classes.station


#######################################################################
#Flask Setup
#######################################################################
app = Flask(__name__)

#######################################################################
# Flask Routes
#######################################################################

@app.route("/")
def welcome():
    """List available API routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session and query precipation and date data
    session = Session(engine)

    precip_data = session.query(measurement.date, measurement.prcp).all()

    session.close()

    #create dictionary from row data and append to a list
    precip = []
    for date, prcp in precip_data:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)
    
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    #create session to pull station information
    session = Session(engine)
    
    stat_data = session.query(station.station).all()

    session.close()

#create dictionary from row data and append to a list
    stations = []
    for row in stat_data:
        station_dict = {}
        station_dict["station"] = row
        stations.append(station_dict)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #create session to pull last year of data for most active station
    session = Session(engine)
    
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    tobs_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year).\
        filter(measurement.station =='USC00519281').\
        order_by(measurement.date).all()

    session.close()

    #create dictionary from row data and append to a list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def temp_stats(start):
    """Pull temperature data for all dates greater than or equal to start date"""

    #create session to pull min, max, and avg temp and date data from start date
    session = Session(engine)

    start_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

    session.close()

    # Create a dictionary to hold start data
    stats_start = []
    
    for min, avg, max in start_data:
        stats_start_dict = {}
        stats_start_dict["min"] = min
        stats_start_dict["avg"] = avg
        stats_start_dict["max"] = max
        stats_start.append(stats_start_dict)
   
    return jsonify(stats_start)




@app.route("/api/v1.0/<start>/<end>")
def stat2(start, end):
    session=Session(engine)
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    for dates between the start and end date inclusive."""

    start_end_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    # Create a dictionary to hold start/end data
    start_end_stats = []

    for min, avg, max in start_end_data:
        start_end_stats_dict = {}
        start_end_stats_dict["min"] = min
        start_end_stats_dict["avg"] = avg
        start_end_stats_dict["max"] = max
        start_end_stats.append(start_end_stats_dict)

    return jsonify(start_end_stats)

if __name__ == '__main__':
    app.run(debug=True)

