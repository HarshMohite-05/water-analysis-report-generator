import pandas as pd
import streamlit as st

from components.authentication import require_login
from components.ui_components import page_setup
from config.settings import OFFICES
from services import audit_service, parameter_service, report_service, dataset_service

page_setup('Admin Panel')
user = require_login(admin_only=True)
st.title('Admin Panel')
st.caption('Choose Employees or Clients below to edit an existing record, add a new record, or delete one.')
t_params, t_clients, t_users, t_reports, t_audit = st.tabs(['Parameters', 'Clients', 'Employees', 'Reports', 'Audit log'])


def perform(action):
    # Recheck the live directory immediately before every write.
    try:
        dataset_service.require_admin(user['id'])
        action()
        audit_service.log(user['id'], 'admin_directory_or_parameter_update', '')
        st.success('Saved.')
        st.rerun()
    except (ValueError, PermissionError) as exc:
        st.error(str(exc))
    except Exception:
        st.error('Could not save. Check workbook access and ensure IDs and emails are unique.')


with t_params:
    params = parameter_service.list_parameters(include_inactive=True)
    df = st.data_editor(pd.DataFrame(params), hide_index=True, disabled=['id'], key='pe',
                        column_config={'id': None}, use_container_width=True)
    if st.button('Save parameter changes'):
        perform(lambda: parameter_service.update_parameters(df.fillna('').to_dict('records')))
    with st.form('add_param', clear_on_submit=True):
        c1, c2 = st.columns(2)
        name, unit = c1.text_input('New parameter'), c2.text_input('Unit')
        if st.form_submit_button('Add') and name.strip():
            perform(lambda: parameter_service.add_parameter(name, unit))

employees = dataset_service.employee_directory()
with t_users:
    st.subheader('Edit, add or delete employees')
    st.caption('Employee Data.xlsx is the employee directory. Passwords are never displayed.')
    st.dataframe(pd.DataFrame(employees), hide_index=True, use_container_width=True)
    employee_labels = {e['employee_id']: f"{e['full_name']} ({e['employee_id']})" for e in employees}
    choice = st.selectbox('Employee to manage', ['New employee'] + [e['employee_id'] for e in employees],
                          index=0,
                          format_func=lambda value: employee_labels.get(value, value),
                          help='Select an existing employee to edit the form below. Choose New employee to add one.')
    employee = next((e for e in employees if e['employee_id'] == choice), {})
    with st.form(f'employee_{choice}'):
        employee_id = st.text_input('Employee ID', employee.get('employee_id', ''), disabled=bool(employee))
        full_name = st.text_input('Employee name', employee.get('full_name', ''),
                                  help='Renaming also updates linked client assignments. Employee ID stays unchanged.')
        email = st.text_input('Employee email', employee.get('email', ''))
        contact = st.text_input('Contact number', employee.get('contact_number', ''))
        role = st.text_input('Role', employee.get('role', ''),
                             placeholder='e.g. Intern, Technician, Lab Assistant',
                             help='Enter any job role. Only Admin and Director roles grant access to this Admin Panel.')
        password = st.text_input('Password (leave blank to keep existing)', type='password')
        if st.form_submit_button('Save employee'):
            perform(lambda: dataset_service.save_employee(user['id'], dict(employee_id=employee_id.strip(),
                full_name=full_name.strip(), email=email.strip(), contact_number=contact.strip(), role=role, password=password)))
    if employee:
        st.caption('Deleting removes this employee from the active directory and disables login. Saved reports remain available.')
        confirmed = st.checkbox(f"Confirm deletion of {employee['full_name']}", key=f"delete_employee_{choice}")
        if st.button('Delete employee', disabled=not confirmed):
            perform(lambda: dataset_service.delete_employee(user['id'], employee['employee_id']))

with t_clients:
    st.subheader('Edit, add or delete clients')
    clients = report_service.list_clients()
    st.dataframe(pd.DataFrame(clients), hide_index=True, use_container_width=True)
    choice = st.selectbox('Client to manage', ['New client'] + [c['name'] for c in clients],
                          index=0,
                          help='Select an existing client to edit the form below. Choose New client to add one.')
    client = next((c for c in clients if c['name'] == choice), {})
    with st.form(f'client_{choice}'):
        name = st.text_input('Client name', client.get('name', ''))
        office = st.selectbox('Client office', list(OFFICES), index=list(OFFICES).index(client.get('office') or 'Mumbai Office'))
        address = st.text_area('Client address', client.get('address', ''))
        person = st.text_input('Client contact person', client.get('contact_person', ''))
        email = st.text_input('Client mail ID', client.get('email', ''))
        ids = [e['employee_id'] for e in employees]
        labels = {e['employee_id']: f"{e['full_name']} ({e['employee_id']})" for e in employees}
        assigned = st.selectbox('Assigned employee', ids,
                                index=ids.index(client['assigned_employee_id']) if client.get('assigned_employee_id') in ids else 0,
                                format_func=lambda value: labels[value])
        if st.form_submit_button('Save client'):
            perform(lambda: dataset_service.save_client(user['id'], dict(name=name.strip(), office=office,
                address=address.strip(), contact_person=person.strip(), email=email.strip(), assigned_employee_id=assigned), original_name=client.get('name')))
    if client:
        st.caption('Deleting removes this client from the active directory. Saved reports remain available.')
        confirmed = st.checkbox(f"Confirm deletion of {client['name']}", key=f"delete_client_{choice}")
        if st.button('Delete client', disabled=not confirmed):
            perform(lambda: dataset_service.delete_client(user['id'], client['name']))
    unresolved = [c['name'] for c in clients if not c['assigned_employee_id']]
    if unresolved:
        st.warning('Assign an employee to clients whose technician name could not be matched: ' + ', '.join(unresolved))

with t_reports:
    reports = report_service.list_reports()
    st.caption('Open an existing report to edit its details, results and remarks, then save or regenerate its PDF.')
    if reports:
        st.dataframe(pd.DataFrame(reports), hide_index=True, use_container_width=True)
        selected = st.selectbox('Report to edit', [r['id'] for r in reports],
                                format_func=lambda rid: next(f"{r['report_no']} — {r['client']}" for r in reports if r['id'] == rid))
        if st.button('Edit selected report'):
            dataset_service.require_admin(user['id'])
            st.session_state['open_report_id'] = selected
            st.switch_page('pages/03_Create_Report.py')
    else:
        st.info('No saved reports yet.')

with t_audit:
    st.dataframe(pd.DataFrame(audit_service.recent()), hide_index=True, use_container_width=True)
