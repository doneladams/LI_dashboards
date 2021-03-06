import os
import urllib.parse

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

from app import app, cache, cache_timeout

#Definitions: Job Type Tl Application and TL Amendment/Renewal
#Process Completed: Renewal Review Application, Issue License, Renew License, Amend License, Generate License, Completeness Check, Review Application, Amendment on Renewal
#Not in Status: Draft, More Information Required, Application Incomplete, Payment Pending
#time calculated as time between Scheduled Start Date to today

APP_NAME = os.path.basename(__file__)

print(APP_NAME)

time_categories = ["0-1 Day", "2-5 Days", "6-10 Days", "11 Days-1 Year", "Over 1 Year"]

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset =='df_ind':
            sql = 'SELECT * FROM li_dash_activejobs_tl_ind'
        elif dataset =='df_counts':
            sql = 'SELECT * FROM li_dash_activejobs_tl_counts'
        elif dataset == 'ind_last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_DASH_ACTIVEJOBS_TL_IND'
        elif dataset == 'counts_last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_DASH_ACTIVEJOBS_TL_COUNTS'
        df = pd.read_sql_query(sql=sql, con=con)
    if dataset == 'df_counts':
        df['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
        df.sort_values(by='TIMESINCESCHEDULEDSTARTDATE', inplace=True)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_layout():
    df_counts = dataframe('df_counts')
    counts_last_ddl_time = dataframe('counts_last_ddl_time')
    ind_last_ddl_time = dataframe('ind_last_ddl_time')

    duration_options = []
    for duration in df_counts['TIMESINCESCHEDULEDSTARTDATE'].unique():
        duration_options.append({'label': str(duration), 'value': duration})

    licensetype_options_unsorted = [{'label': 'All', 'value': 'All'}]
    for licensetype in df_counts['LICENSETYPE'].unique():
        if str(licensetype) != "nan":
            licensetype_options_unsorted.append({'label': str(licensetype), 'value': licensetype})

    licensetype_options_sorted = sorted(licensetype_options_unsorted, key=lambda k: k['label'])

    return html.Div([
        html.H1(
            'Active Jobs With Completed Completeness Checks',
            style={'margin-top': '10px'}
        ),
        html.H1(
            '(Trade Licenses)',
            style={'margin-bottom': '50px'}
        ),
        html.Div([
            html.Div([
                html.P('Time Since Scheduled Start Date of Process'),
                dcc.Dropdown(
                    id='duration-dropdown',
                    options=duration_options,
                    multi=True
                ),
            ], className='four columns'),
            html.Div([
                html.P('License Type'),
                dcc.Dropdown(
                    id='licensetype-dropdown',
                    options=licensetype_options_sorted,
                    value='All',
                    searchable=True
                ),
            ], className='six columns'),
        ], className='dashrow filters'),
        html.Div([
            dcc.Graph(
                id='my-graph',
                config={
                    'displayModeBar': False
                },
                figure=go.Figure(
                    data=[
                        go.Bar(
                            x=df_counts[df_counts['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                            y=df_counts[df_counts['JOBTYPE'] == 'Application']['JOBCOUNTS'],
                            name='Application',
                            marker=go.bar.Marker(
                                color='rgb(55, 83, 109)'
                            )
                        ),
                        go.Bar(
                            x=df_counts[df_counts['JOBTYPE'] == 'Amend/Renew']['TIMESINCESCHEDULEDSTARTDATE'],
                            y=df_counts[df_counts['JOBTYPE'] == 'Amend/Renew']['JOBCOUNTS'],
                            name='Amendment/Renewal',
                            marker=go.bar.Marker(
                                color='rgb(26, 118, 255)'
                            )
                        )
                    ],
                    layout=go.Layout(
                        xaxis=dict(
                            title='Time Since Scheduled Start Date of Process'
                        ),
                        yaxis=dict(
                            title='Active Trade License Jobs'
                        ),
                        showlegend=True,
                        legend=go.layout.Legend(
                            x=.75,
                            y=1
                        )
                    )
                )
            )
        ], style={'margin-left': 'auto', 'margin-right': 'auto', 'float': 'none'},
        className='nine columns'),
        html.P(f"Data last updated {counts_last_ddl_time['LAST_DDL_TIME'].iloc[0]}", className = 'timestamp', style = {
        'text-align': 'center'}),
        html.Div([
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=[{}],
                        filterable=True,
                        sortable=True,
                        selected_row_indices=[],
                        editable=False,
                        id='Man001ActiveJobsTL-table'
                    )
                ], style={'text-align': 'center'}),
                html.Div([
                    html.A(
                        'Download Data',
                        id='Man001ActiveJobsTL-download-link',
                        download='Man001ActiveJobsTL.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'})
            ], style={'margin-top': '70px', 'margin-bottom': '50px'})
        ], className='dashrow'),
        html.P(f"Data last updated {ind_last_ddl_time['LAST_DDL_TIME'].iloc[0]}", className = 'timestamp', style = {
        'text-align': 'center'}),
        html.Details([
            html.Summary('Query Description'),
            html.Div(
                'Trade license application or amend/renew jobs that have a completed process of "Renewal Review Application",'
                ' "Issue License", "Renew License", "Amend License", "Generate License", "Completeness Check", '
                '"Review Application", or "Amendment or Renewal"; but haven\'t been completed and don\'t have a status of '
                '"More Information Required", "Payment Pending", "Application Incomplete", or "Draft" (i.e. have a status '
                'of "Distribute", "In Adjudication", "In Review", or "Submitted").')
        ])
    ])

layout = update_layout

def get_data_object(duration, license_type):
    df_selected = dataframe('df_ind')
    if duration is not None:
        if isinstance(duration, str):
            df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'].isin(duration)]
            elif len(duration) == 1:
                df_selected = df_selected[df_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration[0]]
    if license_type != "All":
        df_selected = df_selected[df_selected['LICENSETYPE'] == license_type]
    return df_selected.drop(['PROCESSID'], axis=1)

def update_counts_graph_data(duration, license_type):
    df_counts_selected = dataframe('df_counts')
    if duration is not None:
        if isinstance(duration, str):
            df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration]
        elif isinstance(duration, list):
            if len(duration) > 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'].isin(duration)]
            elif len(duration) == 1:
                df_counts_selected = df_counts_selected[df_counts_selected['TIMESINCESCHEDULEDSTARTDATE'] == duration[0]]
    if license_type != "All":
        df_counts_selected = df_counts_selected[df_counts_selected['LICENSETYPE'] == license_type]
    df_grouped = (df_counts_selected.groupby(by=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE'])['JOBCOUNTS']
                  .sum()
                  .reset_index())
    df_grouped['JOBTYPE'] = df_grouped['JOBTYPE'].astype(str)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    for time_cat in time_categories:
        if time_cat not in df_grouped[df_grouped['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'].values:
            df_missing_time_cat = pd.DataFrame([['Application', time_cat, 0]], columns=['JOBTYPE', 'TIMESINCESCHEDULEDSTARTDATE', 'JOBCOUNTS'])
            df_grouped = df_grouped.append(df_missing_time_cat, ignore_index=True)
    df_grouped['TIMESINCESCHEDULEDSTARTDATE'] = pd.Categorical(df_grouped['TIMESINCESCHEDULEDSTARTDATE'], time_categories)
    return df_grouped.sort_values(by='TIMESINCESCHEDULEDSTARTDATE')

@app.callback(
    Output('my-graph', 'figure'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_graph(duration, license_type):
    df_counts_updated = update_counts_graph_data(duration, license_type)
    return {
        'data': [
            go.Bar(
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['TIMESINCESCHEDULEDSTARTDATE'],
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Application']['JOBCOUNTS'],
                name='Application',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amend/Renew']['TIMESINCESCHEDULEDSTARTDATE'],
                y=df_counts_updated[df_counts_updated['JOBTYPE'] == 'Amend/Renew']['JOBCOUNTS'],
                name='Amendment/Renewal',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        'layout': go.Layout(
            xaxis=dict(
                title='Time Since Scheduled Start Date of Process'
            ),
            yaxis=dict(
                title='Active Trade License Jobs'
            ),
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            )
        )
    }

@app.callback(
    Output('Man001ActiveJobsTL-table', 'rows'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_table(duration, license_type):
    df = get_data_object(duration, license_type)
    return df.to_dict('records')


@app.callback(
    Output('Man001ActiveJobsTL-download-link', 'href'),
    [Input('duration-dropdown', 'value'),
     Input('licensetype-dropdown', 'value')])
def update_download_link(duration, license_type):
    df = get_data_object(duration, license_type)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string