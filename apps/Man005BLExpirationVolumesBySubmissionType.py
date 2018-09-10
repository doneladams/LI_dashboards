import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table_experiments as table
import urllib.parse

from app import app, con

with con() as con:
    sql="""SELECT lic.licensenumber "LicenseNumber", lt.name "LicenseType", lg.expirationdate "ExpirationDate",( CASE WHEN ap.createdby LIKE '%2%' THEN 'Online' WHEN ap.createdby LIKE '%3%' THEN 'Online' WHEN ap.createdby LIKE '%4%' THEN 'Online' WHEN ap.createdby LIKE '%5%' THEN 'Online' WHEN ap.createdby LIKE '%6%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%9%' THEN 'Online' WHEN ap.createdby = 'PPG User' THEN 'Online' WHEN ap.createdby = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END) "CreatedByType", ap.externalfilenum "JobNumber", jt.name "JobType", Extract(month FROM ap.createddate) || '/' ||Extract(day FROM ap.createddate) || '/' || Extract(year FROM ap.createddate) "JobCreatedDate", Extract(month FROM ap.completeddate) || '/' ||Extract(day FROM ap.completeddate) || '/' || Extract(year FROM ap.completeddate) "JobCompletedDate", ( CASE WHEN jt.description LIKE 'Business License Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle=' ||apl.applicationobjectid ||'&processHandle=&paneId=1239699_151' END ) "JobLink" FROM lmscorral.bl_licensetype lt, ( select licensenumber, licensetypeobjectid, licensegroupobjectid, objectid, mostrecentissuedate from lmscorral.bl_license where mostrecentissuedate >= '01-JAN-2015' ) lic, ( select expirationdate, objectid from lmscorral.bl_licensegroup where expirationdate >= '01-JAN-2015' ) lg, query.r_bl_application_license apl, query.j_bl_application ap, query.o_jobtypes jt WHERE lt.objectid = lic.licensetypeobjectid (+) AND lic.licensegroupobjectid = lg.objectid (+) AND lic.objectid = apl.licenseobjectid (+) AND apl.applicationobjectid = ap.objectid(+) AND ap.jobtypeid = jt.jobtypeid (+) AND lic.MostRecentIssueDate between (ap.CompletedDate -1) and (ap.CompletedDate +1) AND ap.statusid LIKE '1036493' ---Only approved ones AND ap.externalfilenum LIKE 'BA%' ---? AND lic.licensetypeobjectid != 10571 ---don't include activity licenses b/c they don't have expiration dates. Not sure this actually impacts the data though UNION SELECT lic.licensenumber "LicenseNumber", lt.name "LicenseType", lg.expirationdate "ExpirationDate", ( CASE WHEN ar.createdby LIKE '%2%' THEN 'Online' WHEN ar.createdby LIKE '%3%' THEN 'Online' WHEN ar.createdby LIKE '%4%' THEN 'Online' WHEN ar.createdby LIKE '%5%' THEN 'Online' WHEN ar.createdby LIKE '%6%' THEN 'Online' WHEN ar.createdby LIKE '%7%' THEN 'Online' WHEN ar.createdby LIKE '%7%' THEN 'Online' WHEN ar.createdby LIKE '%9%' THEN 'Online' WHEN ar.createdby = 'PPG User' THEN 'Online' WHEN ar.createdby = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END ) "CreatedByType", ar.externalfilenum "JobNumber", jt.name "JobType", Extract(month FROM ar.createddate) || '/' ||Extract(day FROM ar.createddate) || '/' || Extract(year FROM ar.createddate) "JobCreatedDate", Extract(month FROM ar.completeddate) || '/' ||Extract(day FROM ar.completeddate) || '/' || Extract(year FROM ar.completeddate) "JobCompletedDate", ( CASE WHEN jt.description LIKE 'Amendment/Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle=' ||arl.amendrenewid ||'&processHandle=&paneId=1243107_175' END ) "JobLink" FROM lmscorral.bl_licensetype lt, ( select licensenumber, licensetypeobjectid, licensegroupobjectid, objectid, mostrecentissuedate from lmscorral.bl_license where mostrecentissuedate >= '01-JAN-2015' ) lic, ( select expirationdate, objectid from lmscorral.bl_licensegroup where expirationdate >= '01-JAN-2015' ) lg, query.r_bl_amendrenew_license arl, query.j_bl_amendrenew ar, query.o_jobtypes jt WHERE lt.objectid = lic.licensetypeobjectid (+) AND lic.licensegroupobjectid = lg.objectid (+) AND lic.objectid = arl.licenseid (+) AND arl.amendrenewid = ar.objectid (+) AND ar.jobtypeid = jt.jobtypeid (+) AND lic.MostRecentIssueDate between (ar.CompletedDate -1) and (ar.CompletedDate +1) AND ar.statusid LIKE '1036493' AND ar.externalfilenum LIKE 'BR%' AND lic.licensetypeobjectid != 10571 ---don't include activity licenses b/c they don't have expiration dates. Don't think this actually impacts the data though"""
    df = pd.read_sql(sql,con)
    
#make sure ExpirationDate column is of type datetime so that filtering of dataframe based on date can happen later
df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], errors = 'coerce')

def get_data_object(selected_start, selected_end):
    df_selected = df[(df['ExpirationDate']>=selected_start)&(df['ExpirationDate']<=selected_end)]
    df_selected['ExpirationDate'] = df_selected['ExpirationDate'].dt.strftime('%m/%d/%Y')  #change date format to make it consistent with other dates
    df_selected['JobType'] = df_selected['JobType'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    return df_selected

def count_jobs(selected_start, selected_end):
    df_countselected = df[(df['ExpirationDate']>=selected_start)&(df['ExpirationDate']<=selected_end)]
    df_counter = df_countselected.groupby(by=['JobType', 'LicenseType'], as_index=False).size().reset_index()
    df_counter = df_counter.rename(index=str, columns={"JobType": "JobType", "LicenseType": "LicenseType", 0: "Count"})
    df_counter['JobType'] = df_counter['JobType'].map(lambda x: str(x)[5:]) #strip first five characters "j_BL_" just to make it easier for user to read
    return df_counter

layout = html.Div(children=[
                    html.H1(children='Business License Expirations by Type'),
                    html.Div(children='Please Select Date Range (Expiration Date)'),
                dcc.DatePickerRange(
                    id='Man005BL-my-date-picker-range',
                    start_date=datetime(2018, 1, 1),
                    end_date=datetime.now()
                ),
                html.Div([
                    html.A(
                        'Download Counts Data',
                        id='Man005BL-count-table-download-link',
                        download='Man005BLExpirationVolumesBySubmissionType-counts.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'}),
                table.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    columns=["JobType", "LicenseType", "Count"],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='Man005BL-count-table'
                ),
                html.Div([
                    html.A(
                        'Download Business License Data',
                        id='Man005BL-table-download-link',
                        download='Man005BLExpirationVolumesBySubmissionType-alldata.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'}),
                table.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='Man005BL-table')
                ])

@app.callback(Output('Man005BL-count-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def updatecount_table(start_date, end_date):
    df_counts = count_jobs(start_date, end_date)
    return df_counts.to_dict('records')

@app.callback(
            Output('Man005BL-count-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_count_table_download_link(start_date, end_date):
    df = count_jobs(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('Man005BL-table', 'rows'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_inv = get_data_object(start_date, end_date)
    return df_inv.to_dict('records')

@app.callback(
            Output('Man005BL-table-download-link', 'href'),
            [Input('Man005BL-my-date-picker-range', 'start_date'),
            Input('Man005BL-my-date-picker-range', 'end_date')])
def update_table_download_link(start_date, end_date):
    df = get_data_object(start_date, end_date)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string