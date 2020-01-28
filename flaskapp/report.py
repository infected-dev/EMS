from flask import Blueprint, render_template, request, url_for, redirect, flash
from .models import Vehicle, Visitor, Department, CompanyTimesheet, CompanyVehicle, Timesheet_Visitor, Activity, Employee
from datetime import datetime, timedelta
from flaskapp import db


report = Blueprint('report', __name__)

@report.route('/dashbaord')
def dashboard():
    today = datetime.now().date()
    ## Daily Vehicles and Visitors Count ##
    
    query_visitors_today = Timesheet_Visitor.query.filter_by(date=today, plant_id=3).count()
    
    ## All Vheicles and Visitor Count ##
   
    query_visitors_all = Timesheet_Visitor.query.count()

    ## Department Count Queries ##
    departments = { d.id : d.department_name for d in Department.query.all() } 
    dept_count = []
    lessthan_dept_count = []
    for i in departments:
        count = Activity.query.filter_by(visiting_department=i).count()
        if count > 20:
            dept_count.append([departments[i], count])
        elif count > 2 and count < 20:
            lessthan_dept_count.append([departments[i], count])

    ## Date Wise Count Queries for charts ##

    legend = 'Total Visitors by Date'
    dates = [r.date for r in db.session.query(Timesheet_Visitor.date).distinct()]
    dates.pop()
    dates = sorted(dates)
    
    total_count = []
    for i in dates: 
        count = Timesheet_Visitor.query.filter_by(date=i).count()
        total_count.append([i.strftime("%x"), count])
    
    return render_template('Dashboards/dashboard-visitors.html',legend=legend, total_count=total_count, 
        query_visitors_all=query_visitors_all, query_visitors_today=query_visitors_today, dept_count=dept_count, lessthan_dept_count=lessthan_dept_count)


@report.route('/dashbaord/vehicles')
def dashboard_vehicle():
    today = datetime.now().date()
    ## Daily Vehicles and Visitors Count ##
    query_vehicles_today = Vehicle.query.filter_by(VeEntryDate=today).count()
    query_vehicles_all = Vehicle.query.count()

    legend = 'Total Outside Vehicles by Date'
    dates = [r.VeEntryDate for r in db.session.query(Vehicle.VeEntryDate).distinct()]
    total_count = []
    for i in dates: 
        count = Vehicle.query.filter_by(VeEntryDate=i).count()
        total_count.append([i.strftime("%d/%m/%Y"), count])


    return render_template('Dashboards/dashboard-vehicles.html',legend=legend, total_count=total_count, query_vehicles_all=query_vehicles_all, 
        query_vehicles_today=query_vehicles_today)


@report.route('/report/visitors')
def report_main():
    error = None
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    departments = Department.query.filter_by(plant_id=3).all()
    date = yesterday
    visitors = Timesheet_Visitor.query.filter_by(date=today, plant_id=3).all()
    vehicles = Vehicle.query.all()
    vis = Visitor.query.filter_by(plant_id=3).all()
    return render_template('Reports/report-visitors.html',departments=departments, date=date.strftime('%d-%b-%Y')
    , visitors=visitors, vehicles=vehicles, error=error, vis=vis)


@report.route('/report/vehicles')
def report_vehicles():
    depts = Department.query.filter_by(plant_id=3).all()
    query_vehicles_outside = Vehicle.query.all()
    return render_template('Reports/report-vehicles.html',query_vehicles_outside=query_vehicles_outside, 
       depts=depts)


@report.route('/report/vehicles/mill/')
def mill_report():
    if request.args:
        query_vehicles_mill = CompanyTimesheet.query.all()  
        query_comp_vehicles = CompanyVehicle.query.all()    
        comp_veh_id = request.args['comp_vehicle']
        comp_vehicle = CompanyVehicle.query.get(comp_veh_id)
        timesheet= comp_vehicle.timesheet   
        return render_template('Reports/report-mill.html',timesheet=timesheet,query_comp_vehicles=query_comp_vehicles,
        query_vehicles_mill=query_vehicles_mill,
       )
    depts = Department.query.all()
    query_vehicles_mill = CompanyTimesheet.query.all()
    query_comp_vehicles = CompanyVehicle.query.all()
    return render_template('Reports/report-mill.html',depts=depts, query_comp_vehicles=query_comp_vehicles, 
        query_vehicles_mill=query_vehicles_mill)


@report.route('/print-report', methods=['POST'])
def report_print():
    count = 0
    if request.form:
        print_id = request.form.get('printid')
        date = request.form.get('date')
        if date:
            date = datetime.strptime(
                    date, '%Y-%m-%d').date()
        if print_id == '1':
            title = 'Visitor Records'
            query = Timesheet_Visitor.query.filter_by(date=date, plant_id=3).all()
            count = len(query)
            count_extra = 0
            for i in query:
                if i.extras is not None :
                    a = i.extras
                    count_extra = count_extra + a

            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title, count_extra=count_extra)
        elif print_id == '2':
            title = 'Outside Vehicle Records'
            query = Vehicle.query.filter_by(VeEntryDate=date).all()
            count = len(query)
            return render_template('Reports/report-vehicles-print.html',  query=query,count=count, title=title, date=date)
        elif print_id == '22':
            dept_check = request.form.get('deptcheck')
            if dept_check:
                 title = 'Outside Vehicle Record Sorted by Dept'
                 query = Vehicle.query.filter_by(VeEntryDate=date).all()
                 count = len(query)
                 return render_template('Reports/report-vehicles-print.html', query=query,count=count, title=title, date=date)
            else:
                title = 'Outside Vehicle Records by Department'
                dept_id = int(request.form.get('deptselect'))
                query = Vehicle.query.filter(Vehicle.VeEntryDate == date, Vehicle.visited_department == dept_id).all()
                count = len(query)
                department = Department.query.get(dept_id)
                return render_template('Reports/report-vehicles-print.html', query=query,count=count, title=title, date=date, department=department)
        elif print_id == '3':
            title = 'Mill Vehicle Records'
            query = CompanyTimesheet.query.filter_by(date=date).all()
            count = len(query)
            return render_template('Reports/report-vehicles-print.html', query=query, title=title,count=count, date=date)
        elif print_id == '8':
            title = 'Visitor Records Sorted by Employee Visited'
            query = Timesheet_Visitor.query.filter_by(date=date, plant_id=3).all()
            count = len(query)
            count_extra = 0
            for i in query:
                if i.extras is not None :
                    a = i.extras
                    count_extra = count_extra + a
            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title, count_extra=count_extra)
        elif print_id == '10':
            title = 'Visitor Records Sorted By Department'
            query = Timesheet_Visitor.query.filter_by(date=date, plant_id=3).all()
            count = len(query)
            
            return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title)
        elif print_id == '9': 
            dept_check = request.form.get('deptcheck')
            if dept_check:
                title = 'Visitor Records Sorted by Department'
                query = Timesheet_Visitor.query.filter_by(date=date, plant_id=3).all()
                count = len(query)
                
                return render_template('Reports/report-visitors-print.html',count=count, query=query, date=date, title=title)
            else:
                department_id = int(request.form.get('department'))
                department = Department.query.get(department_id)
                query = Timesheet_Visitor.query.filter_by(date=date, plant_id=3).all()
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
            
             query = Timesheet_Visitor.query.filter(Timesheet_Visitor.date.between(date, date_2),Timesheet_Visitor.plant_id != 4)
             count = len(query)
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

        elif print_id == '16':
            title = 'Consolidated Visitor to Department Report'
            date_2 = datetime.strptime(
                request.form.get('date2'), '%Y-%m-%d').date() 
            department = request.form.get('department')
            
            query = db.session.query(Timesheet_Visitor).join(Activity).filter(Timesheet_Visitor.date.between(date, date_2), Activity.visiting_department == department).all()
            
            count = len(query)
            count_extra = 0
            delta = date_2 - date
            for i in query:
                 if i.extras:
                     count_extra += i.extras
            return render_template('Reports/report-visitors-print.html', title=title, count=count, count_extra=count_extra,date=date, date_2=date_2, query=query, delta=delta)



@report.route('/print-slip', methods=['POST'])
def printslip():
    if request.form:
        get_id = int(request.form.get('vi_id'))
        serial = request.form.get('serialno')
        visitor = Timesheet_Visitor.query.filter_by(id=get_id).first()
        return render_template('print-visitor-slip.html', visitor=visitor, serial=serial)


@report.route('/frequentVisitors')
def frequent_visitor():
    freq = []
    visitors = Visitor.query.all()
    for i in visitors:
        if len(i.a_timesheet) >= 2:
            freq.append([i.id,i.name,i.place_from,len(i.a_timesheet)])

    return render_template('Reports/report-visitor-freq.html', freq=freq)

@report.route('/departmentVisitors', methods=['GET','POST'])
def department_visitors():

    timesheet = Timesheet_Visitor.query.all()
    timelog = []
    department = Department.query.all()
    count = 0
    dept_name = '' 
    if request.form:
        dept_id = int(request.form.get('dept_id'))
        dept_name = Department.query.get(dept_id)
        dept_name = dept_name.department_name
        for i in timesheet:
           if i.active.visiting_department == dept_id:
               timelog.append(i)                
    count = len(timelog)

    
    return render_template('Reports/report-visitor-dept.html', department=department, timelog=timelog, count=count, dept_name=dept_name)

@report.route('/employeeVisitors', methods=['GET', 'POST'])
def employee_visitors():

    employees = Employee.query.all()
    timesheet = Timesheet_Visitor.query.all()
    dept_name = ''
    timelog = []
    count = 0
    emp_name = ''
    if request.form:
        emp_id = int(request.form.get('emp_id'))
        emp = Employee.query.get(emp_id)
        dept_name = emp.dept.department_name
        emp_name = emp.employee_name
        for i in timesheet:
            if i.active.visiting_employee == emp_id:
                timelog.append(i)
                
    count = (len(timelog))
    return render_template('Reports/report-visitor-employee.html', employees=employees, dept_name=dept_name, timelog=timelog, emp_name=emp_name, count=count)

@report.route('/vendorVisitor', methods=['GET', 'POST'])
def vendor_visitor():
    vistor_vendor = [r.place_from for r in db.session.query(Visitor.place_from).distinct()]
    ref_ven = []
    vendor=''
    if request.form:
        vendor = request.form.get('vendor_name')
        timesheet = Timesheet_Visitor.query.all()
        ref_ven = []
        for i in timesheet:
            if i.a_timelog.place_from == vendor:
                ref_ven.append(i)

    count = len(ref_ven)
    return render_template('report-visitor-vendor.html', vistor_vendor=vistor_vendor, ref_ven=ref_ven, count=count, vendor=vendor)

@report.route('/frequentOutisdeVehicles', methods=['GET', 'POST'])
def dept_outsidevehicle():
    depts = Department.query.all()
    ref_depts = []
    for i in depts:
        if len(i.outside_vehicles) >=1:
            ref_depts.append(i)
    dept_name = ''
    timelog = ''
    count = 0
    if request.form:
        dept_id = int(request.form.get('outdept_id'))
        department = Department.query.get(dept_id)
        dept_name = department.department_name
        timelog = department.outside_vehicles
    count = len(timelog)
    return render_template('Reports/report-vehicle-outside-dept.html', dept_name=dept_name, timelog=timelog, ref_depts=ref_depts, count=count)

@report.route('/vendorOutsideVehicle', methods=['GET', 'POST'])
def vendor_outsidevehicle():
    log = Vehicle.query.all()
    vendors = [r.VendorName for r in db.session.query(Vehicle.VendorName).distinct()]
    req_log = []
    vendor_name = ''
    if request.form:
        vendor_name = request.form.get('vendor_name')
        for i in log:
            if i.VendorName == vendor_name:
                req_log.append(i)
    count = len(req_log)
    return render_template('Reports/report-vehicle-outside-vendor.html', vendors=vendors, req_log=req_log, vendor_name=vendor_name, count=count)