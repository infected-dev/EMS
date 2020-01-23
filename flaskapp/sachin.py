from flask import Blueprint, redirect, request, url_for, render_template, flash, jsonify
from .models import Visitor, Timesheet_Visitor, AgencyLog, AgencyMast, Department, Location, Employee, Supervisor,\
    Plant,Activity
from . import db    
from .cust_functions import *
from datetime import datetime


sachinapp = Blueprint('sachin', __name__)

@sachinapp.route('/sachinEMS')
def main_sachin():
    today_date = datetime.now().date()
    today_time = (datetime.now().time()).strftime("%H:%M")
    visitors = Visitor.query.filter_by(plant_id=4).all()
    today_visitors = Timesheet_Visitor.query.filter_by(plant_id=4).all()
    employees = db.session.query(Employee).join(Department).filter(Department.plant_id==4).all()
    return render_template('Dataentry/dataentry-visitors.html', visitors=visitors, today_date=today_date,
                           today_visitors=today_visitors, employees=employees)


@sachinapp.route('/sachin/newvisitor', methods=['POST'])
def visitors_post():
   if request.form:
       name = request.form.get('visitorname').upper()
       contact = request.form.get('visitorcontact')
       place_from = request.form.get('visitorcompany')
       #Checks if the Visitor Already existis in the master, if it does only the id is taken over
       if Visitor.query.filter_by(contact=contact).first():
           visitor = Visitor.query.filter_by(contact=contact).first()
       else:
           #Adds new Visitor if it doesnt exist
            visitor = Visitor(name=name, contact=contact, place_from=place_from, plant_id=4)
            db.session.add(visitor)
            db.session.commit()
        
       employee_id = Employee.query.get(int(request.form.get('visiting_employee')))
       emp_id = employee_id.id
       department_id = employee_id.department_id
       visiting_purpose = request.form.get('visitingpurpose')
       activity = Activity(visitor_id=visitor.id, visiting_purpose=visiting_purpose,
            visiting_employee=emp_id, visiting_department=department_id)
       db.session.add(activity)
       db.session.commit()

       date = datetime.strptime(request.form.get('entrydate'), '%Y-%m-%d').date()
       time = datetime.strptime(request.form.get('intime'), '%H:%M').time()
       extras = 0
       if request.form.get('extras'):
           extras = int(request.form.get('extras'))
       timelog = Timesheet_Visitor(visitor_id=visitor.id, activity_id=activity.id, extras=extras , date=date, in_time=time, plant_id=4)
       db.session.add(timelog)
       db.session.commit()
       return redirect(url_for('sachin.main_sachin'))

@sachinapp.route('/sachin/agency')
def agency_sachin():
    return render_template('Agency/agency.html')