import dash
from dash import html, dcc
import pandas
AuthLog = pandas.read_csv("Dateset 2__User_Authentication_Logs.csv")

# SUBFEATURE 1 - TRACKING FAILED LOGIN ATTEMPTS ---
# SUBFEATURE 1 - observing failed login attempts ---
AuthLog['login_timestamp'] = pandas.to_datetime(AuthLog['login_timestamp'])

# SUBFEATURE 2 - TRACKING FAILED GEOLOCATION LOGINS ---
# SUBFEATURE 2 -  grabbing/sorting username and timestamp info from dataset ---
AuthLog_sorted = AuthLog.sort_values(by=['username','login_timestamp'])

AuthLog_sorted['prev_location'] = AuthLog_sorted.groupby('username')['geo_location'].shift(1)
AuthLog_sorted['prev_time'] = AuthLog_sorted.groupby('username')['login_timestamp'].shift(1)

AuthLog_sorted['time_diff'] = (
    AuthLog_sorted['login_timestamp'] - AuthLog_sorted['prev_time']
).dt.total_seconds() / 3600

suspicious_geo=AuthLog_sorted[
    (AuthLog_sorted['geo_location'] != AuthLog_sorted['prev_location']) &
    (AuthLog_sorted['time_diff'] <=6)
]

# SUBFEATURE 1 - TRACKING FAILED LOGIN ATTEMPTS ---
# SUBFEATURE 1 - observing failed login attempts ---

app = dash.Dash(__name__)

fails = AuthLog[AuthLog['login_status'] == 'Failure']
fails_count = fails['username'].value_counts()

# SUBFEATURE 1 - Suspicion Rate
suspicious_users = []

for username, count in fails_count.items():
    if count > 30:
        suspicious_users.append({"username": username, "fail_count": count})

over_30 = pandas.DataFrame(suspicious_users)

def label_suspicion(count):
    if count > 60:
        return 'High'
    elif count > 50:
        return 'Moderate'
    else:
        return 'Mild'

over_30['suspicion_level'] = over_30['fail_count'].apply(label_suspicion)

# SUBFEATURE 2 -  sus users location jumps 
HighSusUser = over_30[over_30['suspicion_level']== 'High']['username'].tolist()

HighSusJump=suspicious_geo[suspicious_geo['username'].isin(HighSusUser)]
jump_count_high=HighSusJump['username'].value_counts().reset_index()
jump_count_high.columns=['username','location_jumps']


# SUBFEATURE 1 - login fail graph creation ---
import plotly.express

graph = plotly.express.bar(
    data_frame=over_30,
    x='username',
    y='fail_count',
    color='suspicion_level',
    title='Anomalous Login Behavoir'
)

# SUBFEATURE 2 -  sus users location jumps graph creation

location_jump_graph=plotly.express.bar(
    data_frame=jump_count_high,
    x='username',
    y='location_jumps',
    title='Highly Suspicious User Login Behavior with Illogical Geolocation Jumps',
    labels={'username': 'Username', 'location_jumps': 'Geolocation Jumps'},
    color='location_jumps'
)



# SUBFEATURE 1 - design app layout ---
app.layout = html.Div([
    html.H1("Failed Login Attempts by User"),
    dcc.Graph(figure=graph),
    # SUBFEATURE 2 -  sus users location jumps app design layout
    html.H1('Location Jumps by Highly-Suspicious Users'),
    dcc.Graph(figure=location_jump_graph)
])



# Run App ---
if __name__ == "__main__":
    app.run(debug=True)
