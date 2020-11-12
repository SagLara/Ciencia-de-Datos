import pandas as pd
from sodapy import Socrata
from flask import Flask,render_template,request

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("www.datos.gov.co", None)

# Example authenticated client (needed for non-public datasets):
# client = Socrata(www.datos.gov.co,
#                  MyAppToken,
#                  userame="user@example.com",
#                  password="AFakePassword")

# First 1000000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
results = client.get("gt2j-8ykr", limit=1000000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)

#prub = results_df.loc[10:20,:]
#prub = results_df.loc[:10,:]
##df = pd.DataFrame({'A': [0, 1, 2, 3, 4], 'B': [5, 6, 7, 8, 9], 'C': ['a', 'b', 'c--', 'd', 'e']})


def resultVirusPais(dataframe, pais):
  importados=dataframe[dataframe['fuente_tipo_contagio']=='Importado']
  up=pais.upper()
  result=importados[importados['pais_viajo_1_nom']==up]
  return result['sexo'].value_counts()




app = Flask(__name__)


def print_df(cant,rango):
    print(cant,rango)
    num=rango+cant
    result=results_df.loc[:10,num]
    return result


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dataframe", methods=["POST"])
def view_df():
    dato = request.form.get("dato")
    opcion = request.form.get("opcion")
    rango=int(dato)+int(opcion)
    print("DESDE: ",dato," HASTA:",rango)
    view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("dataframe.html",nombre=nombre,table=table)
    return view.to_html(header="true", table_id="table")

@app.route("/consultas", methods=["POST"])
def view_consult_pais():
    pais = request.form.get("pais")
    res= resultVirusPais(results_df,str(pais))
    result= pd.DataFrame(res)
    #print("CONSULT: ",dato," HASTA:",rango)
    #view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("dataframe.html",nombre=nombre,table=table)
    return result.to_html(header="true", table_id="table")


if __name__ == "__main__":
    app.run(debug=True, port= 5000) 





    
""" @app.route("/hola/<string:nombre>")
def hola(nombre):
    return f"<h1> hola {nombre}</h1>" """
