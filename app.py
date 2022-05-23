from flask import Flask, render_template, jsonify
import pandas as pd
from six.moves import urllib
import json
 
app = Flask(__name__)
 
@app.route("/data.json")
def data():
    timeInterval = 1000
    data = pd.DataFrame()
    featureList = ['market-price', 
                   'trade-volume']
    for feature in featureList:
        url = "https://api.blockchain.info/charts/"+feature+"?timespan="+str(timeInterval)+"days&format=json"
        data['time'] = pd.DataFrame(json.loads(urllib.request.urlopen(url).read().decode('utf-8'))['values'])['x']*1000
        data[feature] = pd.DataFrame(json.loads(urllib.request.urlopen(url).read().decode('utf-8'))['values'])['y']
    result = data.to_dict(orient='records')
    seq = [[item['time'], item['market-price'], item['trade-volume']] for item in result]
    return jsonify(seq)
 


@app.route("/")
def index():
    return render_template('indexAI.html')

@app.route("/noAI")
def noAI():
    return render_template('indexNoAI.html')    

@app.route("/setRandom")
def getData():
    myserver ="localhost"
    myuser="test123"
    mypassword="test123"
    mydb="aiotdb"
    
    debug =0
    from  pandas import DataFrame as df
    import pandas as pd                     # 引用套件並縮寫為 pd
    import numpy as np

    import pymysql.cursors
    #db = mysql.connector.connect(host="140.120.15.45",user="toto321", passwd="12345678", db="lightdb")
    #conn = mysql.connector.connect(host=myserver,user=myuser, passwd=mypassword, db=mydb)
    conn = pymysql.connect(host=myserver,user=myuser, passwd=mypassword, db=mydb)

    c = conn.cursor()
 

    #====== 執行 MySQL 查詢指令 ======#
    c.execute("update sensors set value = RAND()*1000 where true")
    conn.commit()
    
    c.execute("SELECT * FROM sensors")

    #====== 取回所有查詢結果 ======#
    results = c.fetchall()
    print(type(results))
    print(results[:10])
    if debug:
        input("pause ....select ok..........")

    test_df = df(list(results),columns=['id','time','value','temp','humi','status'])

    print(test_df.head(10))
    result = test_df.to_dict(orient='records')
    seq = [[item['id'], item['time'], item['value'], item['temp'], item['humi'], item['status']] for item in result]
    return jsonify(seq)
    ######### cursor close, conn close
    c.close()
    conn.close()


@app.route("/getPredict")
def getPredict():
    #==== step 1: setup variable ===========
    myserver ="localhost"
    myuser="test123"
    mypassword="test123"
    mydb="aiotdb"
    
    debug =0
    from  pandas import DataFrame as df
    import pandas as pd                     # 引用套件並縮寫為 pd
    import numpy as np

    #step 2: load model  #讀取Model###
    import pickle
    import gzip
    with gzip.open('./model/myModel.pgz', 'r') as f:
        model = pickle.load(f)

    # step 3:　get test data from database        
    

    import pymysql.cursors
    #db = mysql.connector.connect(host="140.120.15.45",user="toto321", passwd="12345678", db="lightdb")
    #conn = mysql.connector.connect(host=myserver,user=myuser, passwd=mypassword, db=mydb)
    conn = pymysql.connect(host=myserver,user=myuser, passwd=mypassword, db=mydb)
    
    c = conn.cursor()
    if debug:
        input("pause.. conn.cursor() ok.......")
    
    #====== 執行 MySQL 查詢指令 ======#
    c.execute("SELECT * FROM sensors")
    
    #====== 取回所有查詢結果 ======#
    results = c.fetchall()
    print(type(results))
    print(results[:10])
    if debug:
        input("pause ....select ok..........")
    
    test_df = df(list(results),columns=['id','time','value','temp','humi','status'])
    
    print(test_df.head(10))
   

    
    testX=test_df['value'].values.reshape(-1,1)
    testY=model.predict(testX)
    print(model.score(testX,testY))
    
    test_df['status']=testY
    print(test_df.head(10))
    
    if debug:
        input("pause.. now show correct one above.......")
    

 
    
    #########################################
    '''
    ##Example 1 ## write back mysql ###############
    threshold =100
    c.execute('update light set status=0 where value>'+str(threshold))
    conn.commit()
    #results = c.fetchall()
    #print(type(results))
    #print(results[:10])
    input("pause ....update ok..........")
    '''
    
    
    ##Example 2 ## write back mysql ###############
    ## make all status =0
    c.execute('update sensors set status=0 where value>0')
    
    ## choose status ==1 have their id available
    id_list=list(test_df[test_df['status']==1].id)
    print(id_list)
                
    for _id in id_list:
        #print('update light set status=1 where id=='+str(_id))
        c.execute('update sensors set status=1 where id='+str(_id))
    
    conn.commit()
    
   
    result = test_df.to_dict(orient='records')
    seq = [[item['id'], item['time'], item['value'], item['temp'], item['humi'], item['status']] for item in result]
    return jsonify(seq)






if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

