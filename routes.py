from flask import Blueprint
from controllers import *

routes = Blueprint('routes', __name__)

# Deklaracje tras
routes.route('/', methods=['GET', 'POST'])(load_start_page)
routes.route('/login', methods=['GET', 'POST'])(login)
routes.route('/dashboard')(dashboard)
routes.route('/register')(register)
routes.route('/submit_register', methods=['POST'])(submit_register)
routes.route('/dashboard_admin')(admin_dashboard)
routes.route('/report')(report)
routes.route('/submit_report', methods=['POST'])(submit_report)
routes.route('/report_success')(report_success)
routes.route('/badges')(badges)
routes.route('/my_reports')(my_reports)
routes.route('/logout')(logout)
routes.route('/save_point', methods=['POST'])(save_point)
routes.route('/change_status/<int:report_id>', methods=['POST'])(lambda report_id: change_status(report_id))
