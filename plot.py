import plotly.graph_objects as go
import pandas as pd
import math
import csv

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

def plot_results():  
    #############################  Pathload Plot ################################
  
    colnames = ['fleet','availbw']

    df0 = pd.read_csv('path_0.csv', names=colnames)
    df1 = pd.read_csv('path_1.csv', names=colnames)
    df2 = pd.read_csv('path_2.csv', names=colnames)

    avail0 = df0.availbw.tolist()
    avail1 = df1.availbw.tolist()
    avail2 = df2.availbw.tolist()

    avail0 = [float(i) for i in avail0]
    avail1 = [float(i) for i in avail1]
    avail2 = [float(i) for i in avail2]

    availres = []
    fleet = []
    i=0

    measures = [avail0, avail1, avail2]
    measures2 = list(filter(lambda var:(len(var)>0),measures))

    lun=len(avail0)
    for x in measures2:
        if(len(x) < lun):
            lun= len(x)
        
    for i in range(lun):
        somma = 0
        for x in measures2:
            somma += x[i]
        availres.append(somma / len(measures2))
        availres[i] = truncate(availres[i],2)
        fleet.append(i)

    print(availres)
    print(fleet)

    result =pd.DataFrame(zip(fleet,availres), columns=['fleet','availbw'])
    result.to_csv('pathresult.csv', index=False)


    dfresult = pd.read_csv('pathresult.csv',names=colnames)
    print(dfresult)

    fig1 = go.Figure()
    # Add traces
    fig1.add_trace(go.Scatter(x=df0['fleet'], y=df0['availbw'],
                        mode='lines+markers',
                        name='first run', 
                        line=dict(color="#7180AC")))
    fig1.add_trace(go.Scatter(x=df1['fleet'], y=df1['availbw'],
                        mode='lines+markers',
                        name='second run',
                        line=dict(color="#793aa1")))
    fig1.add_trace(go.Scatter(x=df2['fleet'], y=df2['availbw'],
                        mode='lines+markers',
                        name='third run',
                        line=dict(color="#61764E")))
    fig1.add_trace(go.Scatter(x=result['fleet'], y=result['availbw'],
                        mode='lines+markers',
                        name='avg',
                        line=dict(color="#C84C09", width=7)))



                            


    ##########################################################################
    #############################  Twamp Plot ################################
    colnames2 = ['Direction','Min','Max','Avg','Jitter','Loss']

    tw0 = pd.read_csv('tw_0.csv')
    tw1 = pd.read_csv('tw_1.csv')
    tw2 = pd.read_csv('tw_2.csv')

    twr0 = tw0.Avg.tolist()
    twr1 = tw1.Avg.tolist()
    twr2 = tw2.Avg.tolist()
    print(twr0)



    twr0 = [float(i.replace("ms","")) for i in twr0]
    twr1 = [float(i) for i in twr1]
    twr2 = [float(i) for i in twr2]
    print(twr0)

    twavg= []

    i=0
    while(i< len(twr0)):
        twavg.append((twr0[i] + twr1[i] + twr2[i]) / 3)
        twavg[i] = truncate(twavg[i],2)
        i+=1

    print(twavg)

    fig2=go.Figure()
    fig2.add_trace(go.Bar(x=tw0['Direction'], y=twr0['Avg'], name='first run', marker_color='#7180AC'))  
    fig2.add_trace(go.Bar(x=tw1['Direction'], y=twr1['Avg'], name='second run', marker_color='#3b508f'))   
    fig2.add_trace(go.Bar(x=tw2['Direction'], y=twr2['Avg'], name='third run', marker_color='#162963'))
    fig2.add_trace(go.Bar(x=tw0['Direction'], y=twavg, name='avg', marker_color='#C84C09'))
    fig2.update_layout(barmode='group', yaxis=dict(rangemode="tozero"), xaxis=dict(rangemode="tozero"), bargroupgap=0.1)   


    with open('results.html', 'w') as f:
        if len(measures2) != 0 :
            f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
    f.close()

    ##########################################################################

plot_results()