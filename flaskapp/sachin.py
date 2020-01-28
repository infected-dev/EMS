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
    log = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id == 4).all()
    supervisors = Supervisor.query.filter_by(plant_id=4).all()
    worktypes = WorkType.query.filter_by(plant_id=4).all()
    agencies = AgencyMast.query.filter_by(plant_id=4).all()
    locations = Location.query.filter_by(plant_id=4).all()
    print(log)
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
            print(loc)
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
    error = None
    today = datetime.now().date()
    
    departments = Department.query.filter_by(plant_id=4).all()
    visitors = Timesheet_Visitor.query.filter(Timesheet_Visitor.date == today, Timesheet_Visitor.plant_id==4).all()
    return render_template('Reports/report-visitors.html', departments=departments, visitors=visitors)

@sachinapp.route('/sachin/report/print', methods=['POST'])
def sachin_report_print():
    count = 0
    if request.form:
        print_id = request.form.get('printid')
        date = datetime.strptime(
                request.form.get('date'), '%Y-%m-%d').date()
        if print_id == '1':
            title = 'Visitor Records'
            query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date==date, Timesheet_Visitor.plant_id == 4).all()
            count = len(query)
            count_extra = 0
            for i in query:
                if i.extras is not None :
                    a = i.extras
                    count_extra = count_extra + a

            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title, count_extra=count_extra)
        elif print_id == '8':
            title = 'Visitor Records Sorted by Employee Visited'
            query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date==date, Timesheet_Visitor.plant_id == 4).all()
            count = len(query)
            count_extra = 0
            for i in query:
                if i.extras is not None :
                    a = i.extras
                    count_extra = count_extra + a
            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title, count_extra=count_extra)
        elif print_id == '10':
            title = 'Visitor Records Sorted By Department'
            query =  Timesheet_Visitor.query.filter(Timesheet_Visitor.date==date, Timesheet_Visitor.plant_id == 4).all()
            count = len(query)
            
            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title)
        elif print_id == '9': 
            dept_check = request.form.get('deptcheck')
            if dept_check:
                title = 'Visitor Records Sorted by Department'
                query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date==date, Timesheet_Visitor.plant_id == 4).all()
                count = len(query)
                
                return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title)
            else:
                department_id = int(request.form.get('department'))
                department = Department.query.get(department_id)
                query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date==date, Timesheet_Visitor.plant_id == 4).all()
                count_extra = 0
               
                filtered_list = []
                for i in query:
                    if i.active.visiting_department == department_id:
                        filtered_list.append(i)
                title = 'Visitors Records by Department'
                count = len(filtered_list)
                return render_template('Reports/report-visitors-print.html',department=department, title=title, count=count, 
                    filtered_list=filtered_list, date=date)
        elif print_id=='13':
             title = 'Consolidated Visitor Report'
             date_2 = datetime.strptime(
                request.form.get('date2'), '%Y-%m-%d').date() 
            
             query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date.between(date, date_2),Timesheet_Visitor.plant_id == 4)
             count = query.count()
             count_extra = 0
             delta = date_2 - date
             for i in query:
                 if i.extras:
                     count_extra += i.extras
             return render_template('Reports/report-visitors-print.html', title=title, count=count, count_extra=count_extra, 
                                    date=date, date_2=date_2, query=query, delta=delta)
        elif print_id=='14':
            title = 'Visitor Wise Report'
            vis_id = int(request.form.get('visitor_id'))
            query = Timesheet_Visitor.query.filter_by(visitor_id=vis_id).all()

            count = len(query)

            count_extra = 0 
            for i in query:
                if i.extras:
                    count_extra += i.extras
            return render_template('Reports/report-visitors-print.html', title=title, count=count, count_extra=count_extra, 
                                    query=query)

@sachinapp.route('/sachin/report/agency')
def report_agency_sachin():
    today = datetime.now().date()
    log = db.session.query(AgencyLog).join(Location).filter(Location.plant_id == 4).all()
    locations = Location.query.filter_by(plant_id=4).all()
    agency_mast = AgencyMast.query.filter_by(plant_id=4).all()
    supervisors = Supervisor.query.filter_by(plant_id=4).all()
    return render_template('Reports/report-agency.html',log=log,
                            locations=locations, agency_mast=agency_mast,
                            supervisors=supervisors)

@sachinapp.route('/sachin/report/agency/print', methods=['POST'])
def sachin_report_agency_print():
        if request.form:
            printid = int(request.form.get('printid'))
            date = request.form.get('date')
            if date:
                date =  datetime.strptime(date, '%Y-%m-%d').date()

            if printid == 1:
                title = 'Agency Records'
                logs = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id == 4).all()
                count = len(logs)
                extras = 0
                for i in logs:
                    if i.manpower:
                        a = i.manpower
                        extras+=a

                return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                        date=date, count=count, extras=extras)
            elif printid == 2:
                check = request.form.get('deptcheck')
                loc = request.form.get('loc')
                if check:
                    title = 'Agency Records Sorted by Location'
                    logs = AgencyLog.query.filter_by(date=date).all()
                else:
                    title = 'Agency Report By Location'
                    if date:
                        logs = AgencyLog.query.filter(AgencyLog.date==date, AgencyLog.location_id==loc).all()
                    else:
                        loc_logs = Location.query.get(loc)
                        logs = loc_logs.log
                    

                count = len(logs)
                extras = 0
                for i in logs:
                    if i.manpower:
                        a = i.manpower
                        extras+=a
                return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                        date=date, count=count, extras=extras)
            elif printid == 3:
                agency_id = request.form.get('agency_name')

                if agency_id:
                    agency_id = int(agency_id)
                    agency_log = AgencyMast.query.get(agency_id)
                    logs = agency_log.log
                    count = len(logs)
                    extras = 0
                    for i in logs:
                        if i.manpower:
                            extras += i.manpower
                    title = 'Agency Report'
                    return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                            count=count, extras=extras)

        elif printid == 5:
            date_2 = datetime.strptime(request.form.get('date2'), '%Y-%m-%d').date()
            title = 'Consolidated Agency Report'
            logs = AgencyLog.query.filter(AgencyLog.date.between(date, date_2))
            extras = 0
            count = logs.count()
            delta = date_2 - date
            for i in logs:
                if i.manpower:
                    extras += i.manpower
            return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                         extras=extras, count=count, date=date, date_2=date_2, delta=delta)
        
        elif printid == 7 :
            date_2 = datetime.strptime(request.form.get('date2'), '%Y-%m-%d').date()
            title = 'Consolidated Agency Report by location'
            location = request.form.get('loc')
            loc = Location.query.get(location)
            logs = AgencyLog.query.filter(AgencyLog.date.between(date, date_2), AgencyLog.location_id == location)
            delta = date_2 - date
            return render_template('Reports/agency-report-print.html', logs=logs, title=title, loc=loc, date=date, date_2=date_2, delta=delta)

        elif printid == 8:
            title = 'Supervisor Report'
            supervisor = request.form.get('supervisor_name')
            logs = AgencyLog.query.filter_by(Supervisor_id=supervisor)
            count = logs.count()
            extra = 0
            for i in logs:
                if i.manpower:
                    extra += i.manpower
            return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                         extra=extra, count=count)

        else:
            flash('Wrong Inputs')
            redirect(url_for('sachin.report_agency_sachin'))
   