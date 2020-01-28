from flask import Blueprint, redirect, request, url_for, render_template, flash, jsonify
from .models import AgencyLog, AgencyMast, Location, Supervisor, WorkType, ToolLog, AgencyPlant
from . import db    
from .cust_functions import *
from datetime import datetime

agencyapp = Blueprint('agencyapp', __name__)



@agencyapp.route('/agency')
def agency_main():
    date = datetime.now().date()
    time = (datetime.now().time()).strftime("%H:%M")
    log = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id != 4).all()
    supervisors = Supervisor.query.filter(Supervisor.plant_id != 4).all()   
    worktypes = WorkType.query.filter(WorkType.plant_id != 4).all() 
    agencies = AgencyMast.query.filter(AgencyMast.plant_id !=4).all()
    locations = Location.query.filter(Location.plant_id != 4).all()
    return render_template('Agency/agency.html', log=log, supervisors=supervisors,
                            worktypes=worktypes, agencies=agencies, 
                            locations=locations, date=date, time=time)



@agencyapp.route('/addagency', methods=['POST'])
def add_log():
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
        remark = request.form.get('remarks')
        supervisor = request.form.get('supervisor').upper()
        location = request.form.get('location').upper()
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        
        in_time = datetime.strptime(request.form.get('intime'), '%H:%M').time()
        out_time = request.form.get('outime')


        if AgencyMast.check_agency(name=agency_name) is None:
            a = AgencyMast(agency_name=agency_name, plant_id=3)
            db.session.add(a)
            db.session.commit()
            a = a.a_id
        else:
            a = AgencyMast.query.filter_by(agency_name=agency_name).first()
            a = a.a_id
            


        if WorkType.check_work(wtype=worktyp) is None:
            wt = WorkType(work_type=worktyp, plant_id=3)
            db.session.add(wt)
            db.session.commit()

            wt = wt.wt_id
        else: 
            wt = WorkType.query.filter_by(work_type=worktyp).first()
            wt = wt.wt_id
            


        if Supervisor.check_supervisor(name=supervisor) is None:
            supe = Supervisor(supervisor_name=supervisor, plant_id=3)
            db.session.add(supe)
            db.session.commit()

            sup = supe.sid
        else:
            supe = Supervisor.query.filter_by(supervisor_name=supervisor).first()
            sup = supe.sid
            

        if Location.check_location(name=location) is None:
            loc = Location(location_name=location, plant_id=3)
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
        return redirect(url_for('agencyapp.agency_main'))


@agencyapp.route('/updateAgency', methods=['POST'])
def update_agency():
    if request.form:
        lid = request.form['lid']
        exit_time = datetime.strptime(
            request.form['exitime'], '%H:%M').time()
        agen_log = AgencyLog.query.get(lid)
        agen_log.out_time = exit_time
        db.session.commit()
        intime = agen_log.in_time
        outtime = agen_log.out_time
        diff = timeobj(intime, outtime)
        agen_log.duration = diff
        db.session.commit()
        return {'status': 'Success'}



@agencyapp.route('/reportAgency', methods=['GET','POST'])
def report_agency():
    today = datetime.now().date()
    log =db.session.query(AgencyLog).join(Location).filter(Location.plant_id != 4).all()
    locations = Location.query.filter(Location.plant_id != 4).all()
    agency_mast =  AgencyMast.query.filter(AgencyMast.plant_id !=4).all()
    supervisors =Supervisor.query.filter(Supervisor.plant_id != 4).all()   
    if request.form:
        al_id = int(request.form.get('al_id'))
        log_item = AgencyLog.query.get(al_id)
        db.session.delete(log_item)
        db.session.commit()
        return redirect(url_for('agencyapp.report_agency'))
    return render_template('Reports/report-agency.html', log=log,
                            locations=locations, agency_mast=agency_mast,
                            supervisors=supervisors)



@agencyapp.route('/printAgencyReport', methods=['POST'])
def print_agency_report():

    if request.form:
        printid = int(request.form.get('printid'))
        date = request.form.get('date')
        if date:
            date =  datetime.strptime(date, '%Y-%m-%d').date()
           
        if printid == 1:
            title = 'Agency Records'
            logs =db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id != 4).all()
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
                logs = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id != 4).all()
            else:
                title = 'Agency Report By Location'
                if date:
                    logs = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date == date, Location.plant_id != 4, Location.lid == loc).all()
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
            date_2 = request.form.get('date2')
            logs = ''
            if agency_id:
                agency_id = int(agency_id)
                if date_2:
                    agency_log = db.session.query(AgencyLog).join(AgencyMast).filter(AgencyLog.date.between(date, date_2), AgencyMast.a_id==agency_id).all()
                    logs = agency_log
                else:
                    agency_log = AgencyMast.query.get(agency_id)
                    logs = agency_log.log
                count = len(logs)
                extras = 0
                for i in logs:
                    if i.manpower:
                        extras += i.manpower
                title = 'Consolidated Report of Agency'

                return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                        count=count, extras=extras, date=date, date_2=date_2)

        elif printid == 5:
            date_2 = datetime.strptime(request.form.get('date2'), '%Y-%m-%d').date()
            title = 'Consolidated Agency Report'
            logs = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date.between(date,date_2), Location.plant_id != 4)
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
            logs = db.session.query(AgencyLog).join(Location).filter(AgencyLog.date.between(date, date_2), AgencyLog.location_id == location)
            delta = date_2 - date
            return render_template('Reports/agency-report-print.html', logs=logs, title=title, loc=loc, date=date, date_2=date_2, delta=delta)

        elif printid == 8:
            title = 'Supervisor Report'
            supervisor = int(request.form.get('supervisor_name'))
           
            logs = AgencyLog.query.filter_by(Supervisor_id=supervisor)
          
            count = logs.count()
            extras = 0
            for i in logs:
                if i.manpower:
                    extras += i.manpower
            return render_template('Reports/agency-report-print.html', logs=logs, title=title,
                                         extras=extras, count=count)

    else:
        flash('Wrong Inputs')
        redirect(url_for('agencyapp.report_agency'))


@agencyapp.route('/freqAgency')
def freq_visitor():

    agency_all = AgencyMast.query.all()
    log = []
    for i in agency_all:
        a = len(i.log)
        log.append([i.agency_name,a])
    return render_template('Reports/report-agency-freq.html', log=log) 


@agencyapp.route('/LocationAgency')
def loc_agency():
    location_all = Location.query.all()

    if request.form:
        loc_id = int(request.form.get('loc'))
        loc = Location.query.get(loc_id)
        logs = loc.log
        return render_template('')


@agencyapp.route('/agencytools', methods=['GET', 'POST'])
def tools_agency():
    today = datetime.now().date()
    log = AgencyLog.query.filter_by(date=today).all()
    tools = ToolLog.query.all()
    if request.form:
        today = datetime.strptime(request.form.get('date'), "%Y-%M-%d").date()
        print(today)
        log = AgencyLog.query.filter_by(date=today).all()
        return render_template('Agency/agency-tools.html', log=log, tools=tools)
    return render_template('Agency/agency-tools.html', log=log, tools=tools)


@agencyapp.route('/editagency', methods=['GET', 'POST'])
def edit_agency():
    date = request.form.get('selected_date')
    if date:
        date = datetime.strptime(date, '%Y-%M-%d').date()
    log = AgencyLog.query.filter_by(date=date).all()
    worktypes = WorkType.query.all()
    supervisors = Supervisor.query.all()
    locations = Location.query.all()
    agencys = AgencyMast.query.all()
    return render_template('Agency/edit-agency.html', log=log, date=date, worktypes=worktypes, supervisors=supervisors, locations=locations,
                            agencys=agencys)


    

@agencyapp.route('/changedata', methods=['POST'])
def chnage_data():
    if request.form:
        log_id = request.form['logid']
        orderno = request.form['order']
        name = request.form['name']
        workers = request.form['workers']
        in_time = request.form['in_time']
        out_time = request.form['out_time']
        work_type = request.form['work_type']
        location = request.form['location']
        supervisor_id = request.form['supervisor']
        agency_id = request.form['agency_id']
        
        if log_id:
            log_id = int(log_id)
            log_item = AgencyLog.query.get(log_id)
        if in_time:
            in_time = datetime.strptime(in_time, '%H:%M').time()
            log_item.in_time = in_time
            db.session.commit()          
        if out_time:
            out_time = datetime.strptime(out_time, '%H:%M').time()
            log_item.out_time = out_time
            db.session.commit()            
        if workers:
            workers = int(workers)
            log_item.manpower = workers
            db.session.commit()           
        if orderno:
            log_item.order = orderno
            db.session.commit()
        if name:
            name = name.upper()
            log_item.contact_person = name
            db.session.commit()
        if work_type:
            if log_item.worktype_id != work_type:
                log_item.worktype_id = work_type
                db.session.commit()

        if location:
            if log_item.location_id is not location:
                log_item.location_id = location
                db.session.commit()

        if supervisor_id:
            if log_item.Supervisor_id is not supervisor_id:
                log_item.Supervisor_id = supervisor_id
                db.session.commit()
        
        if agency_id:
            if log_item.agency_id is not agency_id:
                log_item.agency_id = agency_id
                db.session.commit()

        intime = log_item.in_time
        outtime = log_item.out_time
        diff = timeobj(intime, outtime)
        log_item.duration = diff
        db.session.commit()
        flash('All Updates Done')
    return redirect(url_for('agencyapp.edit_agency'))

@agencyapp.route('/toolbox', methods=['POST'])
def tool_box():
    if request.form:
        agency_id = request.form['agency_id']
        tool_name = request.form['tool_name']
        in_company = request.form['in_company']
        if in_company is None:
            in_company = 0
        tool_log = ToolLog(tool_name=tool_name,
            agency_log_id=agency_id, in_company=in_company)
        db.session.add(tool_log)
        db.session.commit()
        flash('Tool Added') 
    return redirect(url_for('agencyapp.tools_agency'))
        

@agencyapp.route('/get_tool_log', methods=['GET','POST'])
def get_log():
    a_id = request.form['agency_id']
    a_id = int(a_id)
    logs = ToolLog.query.filter_by(agency_log_id=a_id).all()
    log_list = [(t.tool_name,t.in_company) for t in logs]
    return jsonify({'result':log_list})
