import pandas as pd
import plotly.io as pio
import plotly.express as px
pio.renderers.default = "browser"
import matplotlib.pyplot as plt
import glob
import plotly.graph_objects as go
import numpy as np


def load_data(files):
    """ Function that loads all data files in one dataframe"""
    df_created = False
    for file in files:
        df_file = pd.read_csv(file, sep=';')
        if not df_created:
            df = df_file
            df_created = True
        else:
            df = pd.concat([df, df_file], axis=0)
    return df

def join(stations, data):
    """ Function that joins data and stations"""
    new_colnames = ['MEASURE_STATION', 'ESTACION', 'LATITUD', 'LONGITUD']
    stations.columns = new_colnames
    df_agg = pd.merge(data, stations, on='MEASURE_STATION', how='left')
    return df_agg

def add_weeks(df_in):
    day_of_week = 1
    week_of_year = 1
    weeks_out = []
    for i in df_in.index:
        weeks_out.append(week_of_year)
        day_of_week += 1
        if day_of_week > 7:
            # starts new week
            day_of_week = 1
            # increase week number
            week_of_year += 1
    return pd.Series(weeks_out)

def add_month_halves(df_in):
    months = df_in.MONTH.unique()
    for month in months:
        df_filt = df_in.loc[df_in.MONTH == month, :]
        n_month_days = df_filt.shape[0]
        month_out = np.ones(n_month_days)
        month_out[15:] = 2
        if month == 1:
            out = month_out
        else:
            out = np.concatenate((out, month_out))
    return pd.Series(out.astype('int'))

def get_dates(dates):
    out = {}
    for event in dates.keys():
        event_text = '<br>'.join(event.split('_'))
        exact_date = dates[event]['exact_date']
        split_date = dates[event]['approx_date'].split('/')
        month = int(split_date[1])
        month_halve = int(split_date[0][1])
        x = (month-1)*2+1 + (month_halve-1)
        out[event] = {'x': x, 'event_text': event_text, 'date_text': "{}".format(exact_date)}
    return out


if __name__ == "__main__":

    # paths
    data_path = '../data/'
    storing_path = '../output/'
    figure_name = 'COVID19_POLLUTION_INFLUENCE_MADRID'

    # files to load
    files = glob.glob(data_path + "CALIDAD*.csv")
    df_raw = load_data(files).sort_values(by=['YEAR', 'MONTH'])    # load data (load whole data files in one dataframe)
    magnitud = 'NO2'

    ####################################################################################################################
    # PREPARE DATA
    ####################################################################################################################

    day_avg = (df_raw[['MEASURE_STATION', 'YEAR', 'MONTH', 'DAY', magnitud]]
                  .groupby(by=['YEAR', 'MONTH', 'DAY'], as_index=False)
                  .mean())

    df_2020 = day_avg.loc[day_avg.YEAR == 2020, :].reset_index(drop=True)
    # add 'YEAR_WEEK' and 'MONTH_HALVES' features
    df_2020['WEEK'] = add_weeks(df_2020)
    df_2020['MONTH_HALVES'] = add_month_halves(df_2020)

    halves_2020 = df_2020.groupby(by=['MONTH', 'MONTH_HALVES'], as_index=False).mean()
    halves_2020 = halves_2020[['MONTH', 'MONTH_HALVES', 'NO2']]

    df_2015_2019 = day_avg.loc[((day_avg.YEAR >= 2015) & (day_avg.YEAR <= 2019)), :].reset_index(drop=True)
    df_2015_2019 = df_2015_2019.groupby(by=['MONTH', 'DAY'], as_index=False).mean()
    df_2015_2019['MONTH_HALVES'] = add_month_halves(df_2015_2019)

    halves_2015_2019 = df_2015_2019.groupby(by=['MONTH', 'MONTH_HALVES'], as_index=False).mean()
    halves_2015_2019 = halves_2015_2019[['MONTH', 'MONTH_HALVES', 'NO2']]


    ####################################################################################################################
    # DATA TO PLOT
    ####################################################################################################################

    # Remarkable dates
    dates = {'Confinement_start':       {'exact_date': '15/3',
                                        'approx_date': 'F1/3'},     # Month3 (March), fortnight1
             'Confinement_end':         {'exact_date': '28/4',
                                        'approx_date': 'F2/4'},     # Month4 (April), fortnight2
             'New_normality':           {'exact_date': '21/6',
                                         'approx_date': 'F2/6'}}     # Month5 (May), fortnight2

    # Add data
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
             'August', 'September', 'October', 'November', 'December']

    # Average curve
    y_2015_2019 = halves_2015_2019.NO2
    x_2015_2019 = [i for i in range(1,len(y_2015_2019)+1)]
    x0 = x_2015_2019[0]
    xf = x_2015_2019[-1]
    # 2020 curve
    y_2020 = halves_2020.NO2
    x_2020 = [i for i in range(1,len(y_2020)+1)]

    # vertical curves: xvalues
    vertical_data = get_dates(dates)
    xv_1 = vertical_data['Confinement_start']['x']
    xv_2 = vertical_data['Confinement_end']['x']
    xv_3 = vertical_data['New_normality']['x']
    # vertical curves: text
    text_xv_1 = "{}<br>{}".format(vertical_data['Confinement_start']['event_text'],
                                      vertical_data['Confinement_start']['date_text'])
    text_xv_2 = "{}<br>{}".format(vertical_data['Confinement_end']['event_text'],
                                      vertical_data['Confinement_end']['date_text'])
    text_xv_3 = "{}<br>{}".format(vertical_data['New_normality']['event_text'],
                                      vertical_data['New_normality']['date_text'])

    # highlighted area
    partial_x_2015_2019 = x_2015_2019[xv_1-1:xv_3]
    partial_y_2015_2019 = y_2015_2019[xv_1-1:xv_3]
    partial_x_2020 = x_2020[xv_1-1:xv_3]
    partial_y_2020 = y_2020[xv_1-1:xv_3]


    ####################################################################################################################
    # PLOTLY GRAPH
    ####################################################################################################################

    fig = go.Figure()
    # Average curves
    fig.add_trace(go.Scatter(x=x_2020, y=y_2020, name='2020       (Fortnight average levels)',
                             line=dict(color='royalblue', width=4)))
    fig.add_trace(go.Scatter(x=x_2015_2019, y=y_2015_2019, name='2015-2019  (Fortnight average levels)',
                             line=dict(color='darkorange', width=4)))

    # Add vertical lines
    fig.add_shape( dict(type="line", x0=xv_1, y0=0, x1=xv_1, y1=100, line=dict(color="gray", width=2, dash='dot') ))
    fig.add_shape( dict(type="line", x0=xv_2, y0=0, x1=xv_2, y1=100, line=dict(color="gray", width=2, dash='dot') ))
    fig.add_shape( dict(type="line", x0=xv_3, y0=0, x1=xv_3, y1=100, line=dict(color="gray", width=2, dash='dot') ))

    # Fill confinement difference area
    fig.add_trace(go.Scatter(x=partial_x_2015_2019, y=partial_y_2015_2019, fill=None, mode='lines', line_color='darkorange', showlegend=False))
    fig.add_trace(go.Scatter(x=partial_x_2020, y=partial_y_2020, fill='tonexty', mode='lines', opacity=0.1, line_color='royalblue', showlegend=False))

    # Edit the layout
    fig.update_layout(font=dict(family="Courier New, monospace", size=13, color="#3f4441"),
                      title=dict(text='<b>COVID-19 confinement influence: Pollution levels measured in Madrid<b>', y=0.93,
                                 x= 0.5, xanchor='center'),
                      legend=dict(x=0.60, y=0.05, title=dict(text=""), font=dict(size=15)),
                      xaxis=dict(title=dict(text=""),
                                 tickvals=[i+0.5 for i in range(x0, xf, 2)],
                                 ticktext=month,
                                 range=[x0-1, xf+1],
                                 tickfont = dict(family="Courier New, monospace",
                                             size=14)),
                      yaxis=dict(title='Average pollution levels (NO2)',
                                 range=[5, 65]),
                      # add text
                      annotations=[dict(x=xv_1+1.15, y=56, text=text_xv_1, textangle=0, align='left', showarrow=False, font=dict(size=13)),
                                   dict(x=xv_2+1.15, y=56, text=text_xv_2, textangle=0, align='left', showarrow=False, font=dict(size=13)),
                                   dict(x=xv_3+1, y=56, text=text_xv_3, textangle=0, align='left', showarrow=False, font=dict(size=13)),
                                   # fille area text
                                   dict(x=xv_1 + 1.7, y=23, text="<b>Confinement<br>period</b>", showarrow=False, font=dict(color='#1b262c', size=15)),
                                   dict(x=xv_2+2, y=22, text="<b>Progressive<br>return</b>", showarrow=False, font=dict(color='#1b262c', size=15))] )

    fig.show()
    fig.write_html(storing_path + figure_name + '.html')
    print(figure_name, "successfully stored.")