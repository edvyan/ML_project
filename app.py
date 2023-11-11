import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc ## https://pypi.org/project/dash-bootstrap-components/
import joblib
import numpy as np
import pandas as pd  # Import pandas for creating and updating the log table
from dash import dash_table
import os

# Load the trained model
model = joblib.load('model.pkl')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True) 

# Create a DataFrame to store the prediction logs
log_df = pd.DataFrame(columns=['Amount', 'newbalanceOrig', 'newbalanceDest', 'Transaction_Type', 'blacklist_flag_org', 'blacklist_flag_dest', 'Prediction'])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False), 
        html.Div(style={'textAlign': 'center', 'margin-top': '50px', 'margin-bottom': '100px'}, children=[
        dcc.Link('Home Page', href='/', className='nav-button', style={'margin-right': '20px'}), 
        dcc.Link('Prediction Page', href='/prediction', className='nav-button'),  
    ]), 
    

    html.Div(id='page-content'),
    html.A(id='download-link'),  

])

@app.callback(
    Output('export-log-button', 'n_clicks'),
    Input('log-table', 'data_timestamp'),
)
def update_export_button(n_clicks):
    if n_clicks:
        return n_clicks + 1
    return n_clicks

@app.callback(
    Output('download-link', 'href'),
    Input('export-log-button', 'n_clicks'),
    State('log-table', 'data'),
)

def export_log_to_csv(n_clicks, log_data):
    global log_df  # Declare log_df as a global variable
    if n_clicks:
        log_to_export = pd.DataFrame(log_data)

        current_directory = os.getcwd()

        csv_file_path = os.path.join(current_directory, 'log_data.csv')

        log_df.to_csv(csv_file_path, index=False, encoding='utf-8')

        return '/download/' + csv_file_path  
    else:
        return None  

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)

def display_page(pathname):
    if pathname == '/':
        return html.Div([
            html.H1('Welcome to Fraud Detection System', style={'textAlign': 'center', 'marginTop': '50px', 'marginBottom': '50px'}),
            html.P('INSTRUCTION',style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '50px'}),
            html.P('1. In the prediction page, enter all the required information.',style={'textAlign': 'center', 'marginBottom': '10px'}),
            html.P('2. Click "Prediction" to check if the transaction is fraud or not', style={'textAlign': 'center', 'marginBottom': '10px'}),
            html.P('3. Click "prediction page" to start', style={'textAlign': 'center', 'marginBottom': '10px'}),  
            html.P('4. Click "Export logs to csv" save logs', style={'textAlign': 'center', 'marginBottom': '10px'}),            
        ], style={'textAlign': 'left'}) 
    
    elif pathname == '/prediction':
        return html.Div([
            html.Div([
                dcc.Input(id='Amount', type='number', placeholder='Enter the amount', style={'margin-right': '20px'}),
                dcc.Input(id='newbalanceOrig', type='number', placeholder='Enter newbalanceOrig', style={'margin-right': '20px'}),
                dcc.Input(id='newbalanceDest', type='number', placeholder='Enter newbalanceDest'),
            ],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-top': '50px'}),

            html.Div([
                dcc.Dropdown(
                    id='Transaction_Type',
                    options=[
                        {'label': 'CASH_IN', 'value': 'CASH_IN'},
                        {'label': 'CASH_OUT', 'value': 'CASH_OUT'},
                        {'label': 'DEBIT', 'value': 'DEBIT'},
                        {'label': 'PAYMENT', 'value': 'PAYMENT'},
                        {'label': 'TRANSFER', 'value': 'TRANSFER'}],
                    placeholder='Select transaction type',
                    style={'width': '200px', 'margin-right': '20px'}),

                dcc.Dropdown(
                    id='blacklist_flag_org',
                    options=[
                        {'label': 'YES', 'value': '1'},
                        {'label': 'NO', 'value': '0'},],
                    placeholder='Select org status',
                    style={'width': '200px', 'margin-right': '20px'}),

                dcc.Dropdown(
                    id='blacklist_flag_dest',
                    options=[
                        {'label': 'YES', 'value': '1'},
                        {'label': 'NO', 'value': '0'},],
                    placeholder='Select dest status',
                    style={'width': '200px', 'margin-right': '20px'}),
            ],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-top': '50px'}),
            
            html.Div([
                html.Button('Predict', id='predict-button', n_clicks=0, style={'width': '100px', 'margin-top': '10px'}),
                html.Button('Export Log to CSV', id='export-log-button', n_clicks=0, style={'width': '150px', 'margin-top': '10px'}),                
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center', 'height': '10vh'}),

            dcc.Loading(
                    id='log-table-loading',
                    children=[
                        html.H2('Prediction Log', style={'textAlign': 'center'}),
                        dash_table.DataTable(
                            id='log-table',
                            columns=[
                                {'name': 'Amount', 'id': 'Amount'},
                                {'name': 'newbalanceOrig', 'id': 'newbalanceOrig'},
                                {'name': 'newbalanceDest', 'id': 'newbalanceDest'},
                                {'name': 'Transaction_Type', 'id': 'Transaction_Type'},
                                {'name': 'blacklist_flag_org', 'id': 'blacklist_flag_org'},
                                {'name': 'blacklist_flag_dest', 'id': 'blacklist_flag_dest'},
                                {'name': 'Prediction', 'id': 'Prediction'},
                            ],
                            data=log_df.to_dict('records'),
                            style_table={'maxHeight': '300px', 'overflowY': 'auto'},
                        ),
                    ],
                    type='default',
                ),
            html.Div(id='output-container')
        ])
    else:
        return '404 Page Not Found'



# Define callback to update log table when a prediction is made
@app.callback(
    [Output('output-container', 'children'), Output('log-table', 'data')],
    [Input('predict-button', 'n_clicks')],
    [
        Input('Amount', 'value'),
        Input('newbalanceOrig', 'value'),
        Input('newbalanceDest', 'value'),
        Input('Transaction_Type', 'value'),
        Input('blacklist_flag_org', 'value'),
        Input('blacklist_flag_dest', 'value'),
    ]
)

def update_output(n_clicks, Amount, newbalanceOrig, newbalanceDest, Transaction_Type, blacklist_flag_org, blacklist_flag_dest):
    global log_df
    if n_clicks > 0:
        input_values = [Amount, newbalanceOrig, newbalanceDest, Transaction_Type, blacklist_flag_org, blacklist_flag_dest]
        if any(value is None for value in input_values):
            return html.Div('Please enter values', style={'text-align': 'center', 'margin-top': '10px'}), dash.no_update
        else: 
            transaction_type_mapping = {
                'CASH_IN': 0,
                'CASH_OUT': 0,
                'DEBIT': 0,
                'PAYMENT': 0,
                'TRANSFER': 0
            }

            transaction_type_mapping[Transaction_Type] = 1
            transaction_type_encoded = list(transaction_type_mapping.values())

            Amount = float(Amount)
            newbalanceOrig = float(newbalanceOrig)
            newbalanceDest = float(newbalanceDest)
            blacklist_flag_org = float(blacklist_flag_org)
            blacklist_flag_dest = float(blacklist_flag_dest)
        
        features = np.array([[Amount, newbalanceOrig, newbalanceDest] + transaction_type_encoded + [blacklist_flag_org, blacklist_flag_dest]])
        prediction = model.predict(features)

        if log_df is None or log_df.empty:
            log_df = pd.DataFrame(columns=['Amount', 'newbalanceOrig', 'newbalanceDest', 'Transaction_Type', 'blacklist_flag_org', 'blacklist_flag_dest', 'Prediction'])
        
        new_entry = pd.DataFrame([{
            'Amount': Amount,
            'newbalanceOrig': newbalanceOrig,
            'newbalanceDest': newbalanceDest,
            'Transaction_Type': Transaction_Type,
            'blacklist_flag_org': blacklist_flag_org,
            'blacklist_flag_dest': blacklist_flag_dest,
            'Prediction': prediction[0],
            }])
        
        log_df = pd.concat([log_df, new_entry], ignore_index=True)
                # Keep only the last 10 logs
        if len(log_df) > 100:
            log_df = log_df.iloc[-100:]

        # Update the log table data
        log_table_data = log_df.to_dict('records')
        return html.Div(f'Predicted value: {prediction}', style={'text-align': 'center', 'margin-top': '10px'}), log_table_data

    else:
        return html.Div('Please enter values and click to predict', style={'text-align': 'center', 'margin-top': '10px'}), dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
