import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load and prepare the data
data = pd.read_csv(r"C:\Users\goat\Desktop\CYBR KSU\CYBR 7910\Feature 3\Dataset 5__Security_Incident_Reports.csv")
data['report_time'] = pd.to_datetime(data['report_time'], errors='coerce')
data['response_time_minutes'] = pd.to_numeric(data['response_time_minutes'], errors='coerce')
data['is_resolved'] = data['resolution_status'].str.lower() == 'resolved'

# Incident metrics
incident_counts = data['category'].value_counts().reset_index()
incident_counts.columns = ['category', 'incident_count']
avg_response = data.dropna(subset=['response_time_minutes']).groupby('category')['response_time_minutes'].mean().reset_index()
avg_response.columns = ['category', 'avg_response_time']
resolved_percent = data.groupby('category')['is_resolved'].mean().reset_index()
resolved_percent.columns = ['category', 'percent_resolved']

incident_summary = incident_counts.merge(avg_response, on='category').merge(resolved_percent, on='category')
incident_summary = incident_summary.sort_values(by='incident_count', ascending=False)

# Pie chart data
detected_by_counts = data['detected_by'].value_counts().reset_index()
detected_by_counts.columns = ['detected_by', 'count']
resolution_status_counts = data['resolution_status'].value_counts().reset_index()
resolution_status_counts.columns = ['status', 'count']

# Bar chart generator with proper formatting
def create_bar_chart(metric):
    label_map = {
        'incident_count': 'Number of Incidents',
        'avg_response_time': 'Average Response Time (Minutes)',
        'percent_resolved': 'Percent Resolved'
    }
    color_map = {
        'incident_count': 'Blues',
        'avg_response_time': 'Oranges',
        'percent_resolved': 'Greens'
    }

    # Text formatting based on metric
    if metric == 'percent_resolved':
        text_fmt = '.0%'
    elif metric == 'avg_response_time':
        text_fmt = '.0f'  # whole number formatting
    else:
        text_fmt = True  # default

    return px.bar(
        incident_summary,
        x='category',
        y=metric,
        color=metric,
        color_continuous_scale=color_map[metric],
        labels={
            'category': 'Incident Category',
            metric: label_map[metric],
            'percent_resolved': 'Percent Resolved'
        },
        title=label_map[metric] + ' by Incident Category',
        category_orders={'category': incident_summary['category'].tolist()},
        text_auto=text_fmt
    )

# Pie charts
pie_detection_fig = px.pie(
    detected_by_counts,
    names='detected_by',
    values='count',
    title='Detection Method Distribution'
)

pie_resolution_fig = px.pie(
    resolution_status_counts,
    names='status',
    values='count',
    title='Incident Resolution Status',
    color='status',
    color_discrete_map={
        'Not Started': 'red',
        'In Progress': 'yellow',
        'Resolved': 'blue'
    }
)

# Dash app layout
app = dash.Dash(__name__)
app.title = "Incident Dashboard"

app.layout = html.Div(style={
    'backgroundColor': '#1e2a38',
    'padding': '30px',
    'height': '100vh',
    'overflow': 'hidden',
    'fontFamily': 'Arial, sans-serif'
}, children=[
    html.Div(style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'display': 'flex',
        'flexDirection': 'row',
        'gap': '20px',
        'height': '100%'
    }, children=[

        # LEFT: Bar Chart Panel
        html.Div(style={
            'flex': '2',
            'padding': '20px',
            'backgroundColor': '#f9f9f9',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)',
            'maxHeight': '680px',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'space-between'
        }, children=[
            html.Div([
                html.H1("Everything Organics: Security Incident Dashboard", style={
                    'color': '#333',
                    'marginBottom': '20px'
                }),

                html.Label("Select Y-axis Metric:", style={
                    'fontWeight': 'bold',
                    'color': '#444',
                    'marginBottom': '5px'
                }),

                dcc.Dropdown(
                    id='metric-dropdown',
                    options=[
                        {'label': 'Number of Incidents', 'value': 'incident_count'},
                        {'label': 'Average Response Time (Minutes)', 'value': 'avg_response_time'},
                        {'label': 'Percent Resolved', 'value': 'percent_resolved'}
                    ],
                    value='incident_count',
                    clearable=False,
                    style={'marginBottom': '20px'}
                )
            ]),
            dcc.Graph(id='bar-graph', style={'height': '450px'})
        ]),

        # RIGHT: Pie Charts Panel
        html.Div(style={
            'flex': '1',
            'padding': '20px',
            'backgroundColor': '#f9f9f9',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)',
            'maxHeight': '680px',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'space-between'
        }, children=[
            dcc.Graph(figure=pie_detection_fig, style={'height': '320px'}),
            dcc.Graph(figure=pie_resolution_fig, style={'height': '320px'})
        ])
    ])
])

# Interactivity
@app.callback(
    Output('bar-graph', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_bar_chart(selected_metric):
    return create_bar_chart(selected_metric)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
