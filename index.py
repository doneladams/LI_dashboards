import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer
from flask import request
from datetime import datetime

from app import app, server
from apps import (Man001ActiveJobsBL, Man001ActiveJobsTL, Man002ActiveProcessesBL, Man002ActiveProcessesTL,
                  Man004BLJobVolumesBySubmissionType, Man004TLJobVolumesBySubmissionType,
                  Man005BLExpirationDates, Man005TLExpirationDates, Man006OverdueBLInspections, IndividualWorkloads,
                  IncompleteProcessesBL, IncompleteProcessesTL, SLA_BL, SLA_TL, ExpiringLicensesTaxIssues,
                  UninspectedBLsWithCompCheck)
from config import LI_STAT_URL
                  

time = datetime.strftime(datetime.now(), '%I:%M %p %m/%d/%y')

def serve_layout():
    return html.Div([
                html.Nav([
                    html.P('City of Philadelphia | LI Dashboards'),
                    html.Div([
                        html.Button('Miscellaneous', className='dropbtn'),
                        html.Div([
                            html.A('Expiring Licenses with Tax Issues', href='/ExpiringLicensesTaxIssues')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Trade Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Active Jobs', href='/ActiveJobsTL'),
                            html.A('Active Processes', href='/ActiveProcessesTL'),
                            html.A('Job Volumes by Submission Type', href='/JobVolumesBySubmissionTypeTL'),
                            html.A('Expiration Dates', href='/ExpirationDatesTL'),
                            html.A('Individual Workloads', href='/IndividualWorkloads'),
                            html.A('Incomplete Processes', href='/IncompleteProcessesTL'),
                            html.A('SLA License Issuance', href='/SLA_TL')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Business Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Active Jobs', href='ActiveJobsBL'),
                            html.A('Active Processes', href='/ActiveProcessesBL'),
                            html.A('Job Volumes by Submission Type', href='/JobVolumesBySubmissionTypeBL'),
                            html.A('Expiration Dates', href='/ExpirationDatesBL'),
                            html.A('Overdue Inspections', href='/OverdueInspectionsBL'),
                            html.A('Individual Workloads', href='/IndividualWorkloads'),
                            html.A('Incomplete Processes', href='/IncompleteProcessesBL'),
                            html.A('SLA License Issuance', href='/SLA_BL'),
                            html.A('Uninspected Licenses with Completeness Check', href='/UninspectedBLsWithCompCheck')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                ], className='navbar'),
                html.Div([
                    dcc.Location(id='url', refresh=False),
                    html.Div(id='page-content'),
                    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
                ], className='container', style={'margin': 'auto', 'margin-bottom': '45px'}),
                html.Nav([
                    html.Div([
                        html.A('Contact LI GIS Team',
                               href='mailto:ligisteam@phila.gov'),
                        html.A('GitHub',
                               href='https://github.com/CityOfPhiladelphia/LI_dashboards'),
                        html.A('LI Stat',
                               href=LI_STAT_URL),
                    ], style={'width': '500px', 'margin-left': 'auto', 'margin-right': 'auto'})
                ], className='footer-navbar')
            ])

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/ActiveJobsTL':
        return Man001ActiveJobsTL.layout()
    elif pathname == '/ActiveJobsBL':
        return Man001ActiveJobsBL.layout()
    elif pathname == '/ActiveProcessesBL':
        return Man002ActiveProcessesBL.layout()
    elif pathname == '/ActiveProcessesTL':
        return Man002ActiveProcessesTL.layout()
    elif pathname == '/JobVolumesBySubmissionTypeBL':
        return Man004BLJobVolumesBySubmissionType.layout()
    elif pathname == '/JobVolumesBySubmissionTypeTL':
        return Man004TLJobVolumesBySubmissionType.layout()
    elif pathname == '/ExpirationDatesBL':
        return Man005BLExpirationDates.layout()
    elif pathname == '/ExpirationDatesTL':
        return Man005TLExpirationDates.layout()
    elif pathname == '/OverdueInspectionsBL':
        return Man006OverdueBLInspections.layout()
    elif pathname == '/IndividualWorkloads':
        return IndividualWorkloads.layout()
    elif pathname == '/IncompleteProcessesBL':
        return IncompleteProcessesBL.layout()
    elif pathname == '/IncompleteProcessesTL':
        return IncompleteProcessesTL.layout()
    elif pathname == '/SLA_BL':
        return SLA_BL.layout()
    elif pathname == '/SLA_TL':
        return SLA_TL.layout()
    elif pathname == '/ExpiringLicensesTaxIssues':
        return ExpiringLicensesTaxIssues.layout()
    elif pathname == '/UninspectedBLsWithCompCheck':
        return UninspectedBLsWithCompCheck.layout()
    else:
        return Man001ActiveJobsBL.layout()

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 8000), server)
    http_server.serve_forever()
    print('Server has loaded.')
    