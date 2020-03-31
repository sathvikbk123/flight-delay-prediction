import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymongo
import os
import io
import base64
import pandas as pd
from flask import Flask,render_template, request
from catboost import CatBoostRegressor, CatBoostClassifier

app = Flask(__name__)
@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/form', methods=['POST','GET'])
def index1():
    return render_template('form.html')

@app.route('/da', methods=['POST','GET'])
def index4():
    return render_template('form2.html')

@app.route('/data', methods=['POST'])
def data():
    df_flights = pd.read_csv('F:/fun/newsample.csv')
    src_airport = request.form['oa']
    dest_airport = request.form['da']
    try:
        if src_airport != '' and dest_airport != '':
            df_flights = df_flights[(df_flights['DESTINATION_AIRPORT'] == dest_airport) & (df_flights['ORIGIN_AIRPORT'] == src_airport)]
        elif src_airport != '':
            df_flights = df_flights[df_flights['ORIGIN_AIRPORT'] == src_airport]
        elif dest_airport != '':
            df_flights = df_flights[df_flights['DESTINATION_AIRPORT'] == dest_airport]
        if len(df_flights) == 0:
            return "Sorry! No flights Scheduled for the given airports."

    except:
      return "Invalid Airports"

    df_airlines = df_flights['AIRLINE'].tolist()
    dfAvgDelay = df_flights['ARRIVAL_DELAY'].tolist()

    delay = {}
    fast = {}
    d,f = 0,0
    d_,f_ = 0,0
    for i in range(len(df_airlines)):
        if dfAvgDelay[i] < 0:
          try:
            fast[df_airlines[i]] -= dfAvgDelay[i]
            f -= dfAvgDelay[i]
            f_ += 1
          except:
            fast[df_airlines[i]] = 0
        if dfAvgDelay[i] > 0:
          try:
            delay[df_airlines[i]] += dfAvgDelay[i]
            d += dfAvgDelay[i]
            d_ += 1
          except:
            delay[df_airlines[i]] = 0

    for i in fast.keys():
      fast[i] = (fast[i]/f)*100
    for i in delay.keys():
      delay[i] = (delay[i]/d)*100

    delay_flights = list(delay.keys())
    delay_per = list(delay.values())
    fast_flights = list(fast.keys())
    fast_per = list(fast.values())

    img1 = io.BytesIO()
    img2 = io.BytesIO()
    img3 = io.BytesIO()
    img4 = io.BytesIO()


    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis('equal')
    ax.pie(delay_per, labels = delay_flights, autopct='%1.2f%%')
    plt.title("Delayed Arrivals")
    plt.savefig(img1, format='jpg')
    img1.seek(0)
    url1 = base64.b64encode(img1.getvalue()).decode()
    plt.clf()

    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    ax.axis('equal')
    ax.pie(fast_per, labels = fast_flights,autopct='%1.2f%%')
    plt.title("Pre-Scheduled Arrival")
    plt.savefig(img2, format='jpg')
    img2.seek(0)
    url2 = base64.b64encode(img2.getvalue()).decode()
    plt.clf()

    def conv(x):
        return ((x/100)*d)/d_
    delay_per = list(map(conv,delay_per))
    y_pos = np.arange(len(delay_flights))
    plt.bar(delay_flights, delay_per, align='center', alpha=0.5, width = 0.9, color = (0.3,0.1,0.4,0.6))
    plt.xticks(y_pos, delay_flights)
    for i in range(len(delay_flights)):
        plt.text(x = y_pos[i]-0.28 , y = delay_per[i]+0.1, s = "%1.1f" % delay_per[i], size = 6)
    plt.ylabel('Delay (in mins)')
    plt.title('Delayed Arrivals')
    plt.savefig(img3, format='jpg')
    img3.seek(0)
    url3 = base64.b64encode(img3.getvalue()).decode()
    plt.clf()

    def conv1(x):
        return ((x/100)*f)/f_
    fast_per = list(map(conv1,fast_per))
    y_pos = np.arange(len(fast_flights))
    plt.bar(fast_flights, fast_per, align='center', alpha=0.5, width = 0.9, color = (0.3,0.1,0.4,0.6))
    plt.xticks(y_pos, fast_flights)
    for i in range(len(fast_flights)):
        plt.text(x = y_pos[i]-0.28 , y = fast_per[i]+0.045, s = "%1.1f" % fast_per[i], size = 6)
    plt.ylabel('Early Arrival (in mins)')
    plt.savefig(img4, format='jpg')
    img4.seek(0)
    plt.clf()
    url4 = base64.b64encode(img4.getvalue()).decode()

    return render_template('danalysis.html', url1=url1, url2=url2, url3=url3, url4=url4)

@app.route('/test', methods=['POST'])
def index3():
    if request.method=='POST':
        pnr = request.form['ac']
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["flightdb"]
        mycol = mydb["passengers2"]
        myquery = { "PNR": pnr }
        airport = pd.read_csv('airports.csv')
        df = pd.read_csv('last_month.csv')
        mydocs = mycol.find(myquery)
        for mydoc in mydocs:
            df_air = airport[(airport['IATA_CODE'] == mydoc['oair'])]
            origin_lat = df_air['LATITUDE'].iloc[0]
            origin_lon = df_air['LONGITUDE'].iloc[0]
            df_air = airport[(airport['IATA_CODE'] == mydoc['dair'])]
            dest_lat = df_air['LATITUDE'].iloc[0]
            dest_lon = df_air['LONGITUDE'].iloc[0]
            mod_df = df.tail(4000)
            mod_df = mod_df[['AIRLINE', 'ORIGIN_AIRPORT', 'DESTINATION_AIRPORT', 'ARRIVAL_DELAY']]
            delays=[]
            for i in range(4000):
                row=mod_df.iloc[i]
                if row['ORIGIN_AIRPORT'] == mydoc['oair'] and row['AIRLINE'] == mydoc['airline']:
                    delays.append(row['ARRIVAL_DELAY'])
            img = io.BytesIO()
            plt.plot(delays)
            plt.ylabel('Delay (in minutes)')
            plt.xlabel('Previous flights')
            title='Delays in last month from airport: '+ str(mydoc['oair']) + ' and airline: ' + str(mydoc['airline'])
            plt.title(title)
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.clf()
            x = np.array([mydoc['month'],mydoc['airline'],mydoc['schdep'],mydoc['deptime'],mydoc['depdelay'],mydoc['tout'],mydoc['woff'],mydoc['schtime'],mydoc['dist'],mydoc['scharr'],origin_lat,origin_lon,dest_lat,dest_lon,mydoc['etime']])
            model_from_file = CatBoostRegressor()
            model_from_file.load_model("final_unisys", format='cbm')
            y_pred = model_from_file.predict(x)
            if y_pred>=0:
                res="Flight is running late by "+str("{0:.4f}".format(y_pred))
            else:
                res="Flight is arriving early by "+str("{0:.4f}".format(-y_pred))
            return render_template('test.html', valu=res, plot_url=plot_url)

@app.route('/depar', methods=['POST','GET'])
def depar():
    #order of attributes MONTH,AIRLINE,ORIGIN_AIRPORT,DEST_AIRPORT,SCHEDULED_DEPARTURE,SCHEDULED_TIME,DISTANCE,SCHEDULED_ARRIVAL
    unisys_dep_delay_model = CatBoostClassifier()
    unisys_dep_delay_model.load_model("unisys_departure_delay")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    img = io.BytesIO()
    mydb = myclient["flightdb"]
    mycol = mydb["passengers2"]
    airport = pd.read_csv('airports.csv')
    pnr = request.form['in']
    df = pd.read_csv('sample.csv')
    myquery = { "PNR": pnr }
    mydocs = mycol.find(myquery)
    for mydoc in mydocs:
        df_air = airport[(airport['IATA_CODE'] == mydoc['oair'])]
        lat = df_air['LATITUDE'].iloc[0]
        lan = df_air['LONGITUDE'].iloc[0]
        x = np.array([mydoc['month'],mydoc['airline'],mydoc['oair'],mydoc['dair'],mydoc['schdep'],mydoc['schtime'],mydoc['dist'],mydoc['scharr']])
        preds_class = unisys_dep_delay_model.predict(x)
        if preds_class>0:
            op = "No Delay in Departure"
            url = "https://cdn2.iconfinder.com/data/icons/yellow-smiles/1000/Smile-Icons-02_Converted-01-512.png"
            colr = "#007944"
        else:
            op = "Delay in Departure"
            url = "https://cdn0.iconfinder.com/data/icons/emoticons-round-smileys/137/Emoticons-14-512.png"
            colr = "#c81912"
        temp_df=df[df['ORIGIN_AIRPORT']==mydoc['oair']]
        df_month1 = temp_df.groupby(['AIRLINE'])[['target_departure']].mean()
        df_month1.reset_index(inplace=True)
        plt.bar(df_month1['AIRLINE'], df_month1['target_departure'])
        plt.xlabel('AIRLINE')
        plt.ylabel('% of delay')
        plt.savefig(img, format='jpg')
        img.seek(0)
        plt.clf()
        purl = base64.b64encode(img.getvalue()).decode()
        return render_template('depdelay.html', res=op, iurl = url, col=colr, pltu = purl, ap=mydoc['oair'], sla=lat , slo=lan)

@app.route('/arr', methods=['POST','GET'])
def index2():
    return render_template('arrivals.html')

if __name__ == '__main__':
    app.run(debug=True)