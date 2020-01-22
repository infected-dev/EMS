from flask import Blueprint, render_template
from .models import User


base = Blueprint('base', __name__)


@base.route('/')
def index():
    users_md01 = User.query.filter_by(plant_id=3).all()
    users_we01 = User.query.filter_by(plant_id=4).all()
    return render_template('plant_base.html', users_md01=users_md01,
                            users_we01=users_we01) 



    
