import pandas as pd
from sodapy import Socrata
import dateutil
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
results = client.get("gt2j-8ykr", limit=1200000) #12000000

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)

#prub = results_df.loc[10:20,:]
#prub = results_df.loc[:10,:]
##df = pd.DataFrame({'A': [0, 1, 2, 3, 4], 'B': [5, 6, 7, 8, 9], 'C': ['a', 'b', 'c--', 'd', 'e']})
results_df['sexo']=results_df['sexo'].str.upper()
results_df['fecha_reporte_web'] = results_df['fecha_reporte_web'].apply(dateutil.parser.parse)
casos_muertos=results_df[results_df['estado']=='Fallecido']
casos_muertos['fecha_muerte'] = casos_muertos.loc[:,'fecha_muerte'].apply(dateutil.parser.parse)

def resultVirusPais(dataframe, pais):
  importados=dataframe[dataframe['fuente_tipo_contagio']=='Importado']
  up=pais.upper()
  result=importados[importados['pais_viajo_1_nom']==up]
  return result['sexo'].value_counts()

def resultCasosPorDia(results_df,inicio,fin):
  inicio= dateutil.parser.parse(inicio, dayfirst=True)
  fin= dateutil.parser.parse(fin, dayfirst=True)
  resultadosDia=results_df[(results_df['fecha_reporte_web']>=inicio) & (results_df['fecha_reporte_web']<=fin) ]
  resultadosDia=resultadosDia.sort_values('fecha_reporte_web')
  result=resultadosDia.groupby('fecha_reporte_web',as_index=False)['departamento'].count()
  resultado=result.rename(columns={'fecha_reporte_web': 'fecha','departamento': 'Casos'})
  return resultado

def resultMuertosPorDia(results_df,inicio,fin):
  inicio= dateutil.parser.parse(inicio, dayfirst=True)
  fin= dateutil.parser.parse(fin, dayfirst=True)
  resultadosDia=casos_muertos[(casos_muertos['fecha_muerte']>=inicio) & (casos_muertos['fecha_muerte']<=fin) ]
  resultadosDia=resultadosDia.sort_values('fecha_muerte')
  result=resultadosDia.groupby('fecha_muerte',as_index=False)['departamento'].count()
  resultado=result.rename(columns={'fecha_muerte': 'fecha muerte','departamento': 'Fallecidos'})
  return resultado

def resultVirusCiudad(dataframe, ciudad):
  up=ciudad.upper()
  result=dataframe[dataframe['ciudad_municipio_nom']==up]
  return result['sexo'].value_counts()

#def filtros(filtros,dataframe):
# 	fecha_reporte_web 	id_de_caso 	fecha_de_notificaci_n 	departamento 	#
#  departamento_nom 	ciudad_municipio 	ciudad_municipio_nom 	edad 	#
# unidad_medida 	sexo 	fuente_tipo_contagio 	ubicacion 	estado 
# 	pais_viajo_1_cod 	pais_viajo_1_nom 	recuperado 	fecha_inicio_sintomas 
# 	fecha_diagnostico 	fecha_recuperado 	tipo_recuperacion 	per_etn_ 	
# nom_grupo_ 	fecha_muerte

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

    filtros=[]
    todos=False

    if request.method == 'POST':
        print(request.form.getlist('filtros'))
        filtros=request.form.getlist('filtros')
    
    rango=int(dato)+int(opcion)
    print("DESDE: ",dato," HASTA:",rango)

    for f in filtros:
        if f=="all":
            todos=True

    if (todos or filtros==[]):
        view = results_df.loc[int(dato):int(rango),:]
    else:
        view = results_df.loc[int(dato):int(rango),filtros]

    return view.to_html(header="true", table_id="table")

@app.route("/consulta 1", methods=["POST"])
def view_consult_pais():
    pais = request.form.get("pais")
    res= resultVirusPais(results_df,str(pais))
    result= pd.DataFrame(res)
    #print("CONSULT: ",dato," HASTA:",rango)
    #view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("consulta-1.html",pais=pais)
    return result.to_html(header="true", table_id="table")

@app.route("/consulta 2", methods=["POST"])
def view_consult_fecha():
    inicio= request.form.get("inicio")
    fin = request.form.get("fin")
    print("CONSULT: ",inicio," HASTA:",fin)
    res= resultCasosPorDia(results_df,str(inicio),str(fin))
    result= pd.DataFrame(res)
    
    #view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("dataframe.html",nombre=nombre,table=table)
    return result.to_html(header="true", table_id="table")

@app.route("/consulta 3", methods=["POST"])
def view_consult_muertos():
    inicio= request.form.get("inicio")
    fin = request.form.get("fin")
    res= resultMuertosPorDia(results_df,str(inicio),str(fin))
    result= pd.DataFrame(res)
    #print("CONSULT: ",dato," HASTA:",rango)
    #view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("dataframe.html",nombre=nombre,table=table)
    return result.to_html(header="true", table_id="table")

@app.route("/consulta 4", methods=["POST"])
def view_consult_ciudad():
    ciudad = request.form.get("ciudad")
    res= resultVirusCiudad(results_df,str(ciudad))
    result= pd.DataFrame(res)
    #print("CONSULT: ",dato," HASTA:",rango)
    #view = results_df.loc[int(dato):int(rango),:]
    #table=df.to_html(header="true", table_id="table")
    #return render_template("consulta-1.html",pais=pais)
    return result.to_html(header="true", table_id="table")

if __name__ == "__main__":
    app.run(debug=True, port= 5000) 



    
""" @app.route("/hola/<string:nombre>")
def hola(nombre):
    return f"<h1> hola {nombre}</h1>" """
