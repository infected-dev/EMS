from flask import Blueprint, redirect, request, url_for, render_template, flash, jsonify
from .models import Visitor, Timesheet_Visitor, AgencyLog, AgencyMast, Department, Location, Employee, Supervisor, Plant, Activity, WorkType
from . import db    
from .cust_functions import *
from datetime import datetime


sachinapp = Blueprint('sachin', __name__)

@sachinapp.route('/sachinEMS')
def main_sachin():
    today_date = datetime.now().date()
    today_time = (datetime.now().time()).strftime("%H:%M")
    visitors = Visitor.query.filter_by(plant_id=4).all()
    today_visitors = Timesheet_Visitor.query.filter(Timesheet_Visitor.date == today_date, Timesheet_Visitor.plant_id == 4).all()
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
    date = datetime.now().date()
    time = (datetime.now().time()).strftime("%H:%M")
    log = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date,Location.plant_id == 4).all()
    supervisors = Supervisor.query.filter_by(plant_id=4).all()
    worktypes = WorkType.query.filter_by(plant_id=4).all()
    agencies = AgencyMast.query.filter_by(plant_id=4).all()
    locations = Location.query.filter_by(plant_id=4).all()
    return render_template('Agency/agency.html', date=date, supervisors=supervisors, log=log, worktypes=worktypes, agencies=agencies, locations=locations )

@sachinapp.route('/sachin/agency/new', methods=['POST'])
def add_agency_sachin():
   if request.form:
        a = ''
        wt = ''
        sup = ''
        loc = ''
        order_no = request.form.get('orderno')
        agency_name = request.form.get('agencyname').upper()
        total = request.form.get('totalpeople')
        worktyp = request.form.get('worktype')
        represent = request.form.get('rprname')
        vehicle = request.form.get('ifvehicle')
        remark = request.form.get('remark')
        supervisor = request.form.get('supervisor').upper()
        location = request.form.get('location').upper()
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        
        in_time = datetime.strptime(request.form.get('intime'), '%H:%M').time()
        out_time = request.form.get('outime')


        if AgencyMast.check_agency(name=agency_name) is None:
            a = AgencyMast(agency_name=agency_name, plant_id=4)
            db.session.add(a)
            db.session.commit()
            a = a.a_id
        else:
            a = AgencyMast.query.filter_by(agency_name=agency_name).first()
            a = a.a_id
            


        if WorkType.check_work(wtype=worktyp) is None:
            wt = WorkType(work_type=worktyp, plant_id=4)
            db.session.add(wt)
            db.session.commit()

            wt = wt.wt_id
        else: 
            wt = WorkType.query.filter_by(work_type=worktyp).first()
            wt = wt.wt_id
            


        if Supervisor.check_supervisor(name=supervisor) is None:
            supe = Supervisor(supervisor_name=supervisor, plant_id=4)
            db.session.add(supe)
            db.session.commit()

            sup = supe.sid
        else:
            supe = Supervisor.query.filter_by(supervisor_name=supervisor).first()
            sup = supe.sid
            

        if Location.check_location(name=location) is None:
            loc = Location(location_name=location, plant_id=4)
            db.session.add(loc)
            db.session.commit()

            loc = loc.lid
        else:
            loc = Location.query.filter_by(location_name=location).first()
            loc = loc.lid
        

        agency_log = AgencyLog(order=order_no, agency_id=a, worktype_id=wt,
                                contact_person=represent, manpower=total,
                                date=date, in_time=in_time,
                                vehicle_no=vehicle, remarks=remark, 
                                Supervisor_id=sup, location_id=loc)
        db.session.add(agency_log)
        db.session.commit()
        return redirect(url_for('sachin.agency_sachin'))

@sachinapp.route('/sachin/visitor/edit', methods=['GET','POST'])
def edit_visitor_sachin():
    backdate_visitors = ''
    if request.form:
        selected_date = request.form.get('selected_date')
        date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        backdate_visitors = Timesheet_Visitor.query.filter(Timesheet_Visitor.date == date, Timesheet_Visitor.plant_id == 4).all()
    return render_template('Edits/edit-Visitor.html', backdate_visitors=backdate_visitors)

@sachinapp.route('/sachin/agency/edit', methods=['GET', 'POST'])
def edit_agency_sachin():
    date = request.form.get('selected_date')
    if date:
        date = datetime.strptime(date, '%Y-%M-%d').date()
    log = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date,Location.plant_id == 4).all()
    supervisors = Supervisor.query.filter_by(plant_id=4).all()
    worktypes = WorkType.query.filter_by(plant_id=4).all()
    agencys = AgencyMast.query.filter_by(plant_id=4).all()
    locations = Location.query.filter_by(plant_id=4).all()
    return render_template('Agency/edit-agency.html', log=log, date=date, worktypes=worktypes, supervisors=supervisors, locations=locations,
                            agencys=agencys)

@sachinapp.route('/sachin/report/visitor')
def report_visitor_sachin():
    return render_template('Reports/report-visitors.html')

@sachinapp.route('/sachin/report/agency')
def report_agency_sachin():
    return render_template('Reports/report-agency.html')