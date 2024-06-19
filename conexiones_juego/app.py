# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:13:03 2024

@author: pedro
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import random

import requests
from bs4 import BeautifulSoup
import datetime
import json

app = Flask(__name__)
number_to_guess = random.randint(1, 100)

app.secret_key = 'supersecretkey'  # Required for flashing messages

# Recogida de las palabras del día

URL = "https://github.com/Pedrobf99/Conexiones/tree/main"
page = requests.get(URL)

sopita = BeautifulSoup(page.content, "html.parser")

main = sopita.find(id="js-repo-pjax-container")
texto_conexiones = main.find_all("p", dir="auto")

# Recogida de todas las palabras hasta hoy

excel_URL = "https://github.com/Pedrobf99/Conexiones/blob/main/conexiones.csv"
ex_page = requests.get(excel_URL)

ex_sopita = BeautifulSoup(ex_page.content, "html.parser")

#Encontramos la parte del código html con los datos del archivo
ex_texto_conexiones = ex_sopita.find('script', {'data-target': 'react-app.embeddedData'})

# Cargamos los datos recogidos en forma de un json
datos = json.loads(ex_texto_conexiones.string)

#Datos agrupados por día
csv_datos = datos['payload']['blob']['csv']

#Día del primer conexiones histórico
primer_conexiones=datetime.datetime(2024, 4, 26)
#Calculamos que día del conexiones estamos
dia_de_hoy=datetime.datetime.today()
hoy=str((datetime.datetime.today()-primer_conexiones).days+1)


# Nombre de los grupos/temas de cada color
T_amarillo=str(texto_conexiones[1])[26:-5]
T_verde=str(texto_conexiones[2])[23:-5]
T_azul=str(texto_conexiones[3])[22:-5]
T_morado=str(texto_conexiones[4])[24:-5]

# Listas de los conjuntos de palabras de cada color
amarillo = str(texto_conexiones[5])[23:-4].split(",")
verde = str(texto_conexiones[6])[20:-4].split(",")
azul = str(texto_conexiones[7])[19:-4].split(",")
morado = str(texto_conexiones[8])[21:-4].split(",")

colores=[amarillo,verde,azul,morado]

# Conjunto de todas las palabras mezcladas
palabras = amarillo+verde+azul+morado
random.shuffle(palabras)

grid_data = [{'color': '#f0ece4', 'text': palabras[i], 'text_color': '#000000'} for i in range(16)]
clicked_rectangles=[]

total_marcados=[]
color=[]

num_lives=4 
aciertos=0 


def initialize_session():
    session['grid_data'] = grid_data.copy()
    session['clicked_rectangles'] = clicked_rectangles
    session['color'] = color.copy()
    session['aciertos'] = aciertos
    session['num_lives'] = num_lives
    
@app.before_request
def before_request():
    if 'initialized' not in session:
        initialize_session()
        session['initialized'] = True

@app.route('/')
def index():
    session['num_lives'] = num_lives
    return render_template('index.html', grid_data=session['grid_data'], clicked_rectangles=session['clicked_rectangles'], num_lives=session['num_lives'], color=session['color'], aciertos=session['aciertos'])

@app.route('/change_color/<int:index>', methods=['POST'])
def change_color(index):
    clicked_rectangles = session['clicked_rectangles']
    grid_data = session['grid_data']
    
    # Toggle color and text
    if index in clicked_rectangles:
        clicked_rectangles.remove(index)
        grid_data[index]['color'] = '#f0ece4'
        grid_data[index]['text_color'] = '#000000'
    else:
        if len(clicked_rectangles) < 4:
            clicked_rectangles.append(index)
            grid_data[index]['color'] = '#605c4c'
            grid_data[index]['text_color'] = '#ffffff'
        else:
            # If limit reached, do nothing or show an error (optional)
            pass

    return redirect(url_for('index'))

@app.route('/shuffle', methods=['POST'])
def shuffle():
        clicked_rectangles = session['clicked_rectangles']
        grid_data = session['grid_data']
        aciertos = session['aciertos']
        
        palabros=[]
        
        # Recogemos las palabras que estén en la primera fila de la matriz conexiones
        # Vamos a cambiar estas palabras por todas las correctas marcadas
        for i in range(aciertos*4,16):
            palabros.append(grid_data[i]['text'])
        
        random.shuffle(palabros)
        
        marcadas=[]
        if clicked_rectangles:
            for i in clicked_rectangles:
                marcadas.append(grid_data[i]['text'])
        
        clicked_rectangles.clear()
        for i in range(aciertos*4,16):
            grid_data[i]['text'] = palabros[i-aciertos*4] 
            if palabros[i-aciertos*4] in marcadas:
                grid_data[i]['color'] = '#605c4c'
                grid_data[i]['text_color'] = '#ffffff'
                clicked_rectangles.append(i)
            else:
                grid_data[i]['color'] = '#f0ece4'
                grid_data[i]['text_color'] = '#000000'
                
        return redirect(url_for('index'))

@app.route('/desmarcar', methods=['POST'])
def desmarcar():        
        clicked_rectangles = session['clicked_rectangles']
        grid_data = session['grid_data']
        clicked_rectangles.clear()
        for i in range(16):
            grid_data[i]['color'] = '#f0ece4'
            grid_data[i]['text_color'] = '#000000'
        return redirect(url_for('index'))
    
@app.route('/prueba', methods=['POST'])
def prueba():
    clicked_rectangles = session['clicked_rectangles']
    grid_data = session['grid_data']
    aciertos = session['aciertos']
    color = session['color']
    colores = session['colores']
    num_lives = session['num_lives']

    marcadas=[]
    if clicked_rectangles:
        for i in clicked_rectangles:
            marcadas.append(grid_data[i]['text'])
    
    #Comprobamos que el intento tiene exactamente 4 palabras
    if len(marcadas)==4:

        #Recogemos todos los intentos válidos que se vayan realizando
        total_marcados.append(copiar(marcadas))

        if set(marcadas)==set(colores[0]):         
            color.append({"color":"#ffdc6c", "Tema": T_amarillo, "Texto": amarillo[0]+", "+amarillo[1]+", "+amarillo[2]+", "+amarillo[3]})           
            aciertos += 1
            acierto(marcadas)
            
        elif set(marcadas)==set(colores[1]):  
            color.append({"color":"#a0c45a", "Tema": T_verde, "Texto": verde[0]+", "+verde[1]+", "+verde[2]+", "+verde[3]})
            aciertos += 1
            acierto(marcadas)
            
        elif set(marcadas)==set(colores[2]):
            color.append({"color":"#b1c4ef", "Tema": T_azul, "Texto": azul[0]+", "+azul[1]+", "+azul[2]+", "+azul[3]})
            aciertos += 1
            acierto(marcadas)
            
        elif set(marcadas)==set(colores[3]):
            color.append({"color":"#ba81c5", "Tema": T_morado, "Texto": morado[0]+", "+morado[1]+", "+morado[2]+", "+morado[3]})
            aciertos += 1
            acierto(marcadas)  
            
        else:
            num_lives -= 1
            if num_lives>0:
                if len(set(colores[0]) & set(marcadas))==3:
                    flash('Solo te falta uno!')  
                    
                elif len(set(colores[1]) & set(marcadas))==3:
                    flash('Solo te falta uno!')
                elif len(set(colores[2]) & set(marcadas))==3:
                    flash('Solo te falta uno!')
                elif len(set(colores[3]) & set(marcadas))==3:
                    flash('Solo te falta uno!')
                else:
                    pass
                
            if num_lives==0:
                game_over()
                aciertos=4
        
    #Si no tiene cuatro palabras avisamos al jugador de que seleccione 4
    else:
        flash("Selecciona 4 palabras")
        
    if aciertos==4:
        victoria()
        
    return redirect(url_for('index'))

def copiar(marcados):
    # Antes de ganar o perder, cada intento válido se convierté en los emoticonos correspondientes
    compartir=""
    for palabra in marcados:
        if palabra in amarillo:
            compartir=compartir+"🟨"
        elif palabra in verde:
            compartir=compartir+"🟩"
        elif palabra in azul:
            compartir=compartir+"🟦"
        else:
            compartir=compartir+"🟪"
    compartir=compartir+"\n"
    return compartir

def acierto(marcadas):
    clicked_rectangles = session['clicked_rectangles']
    grid_data = session['grid_data']
    aciertos = session['aciertos']
    color = session['color']
    
    conexiones_hz=[]
    
    # Recogemos las palabras que estén en la primera fila de la matriz conexiones
    # Vamos a cambiar estas palabras por todas las correctas marcadas
    for i in range((aciertos-1)*4,aciertos*4):
        conexiones_hz.append(grid_data[i]['text'])
        
    clicked_rectangles.clear()
    no_aciertos = []
    # Comprobamos que las palabras de la primera columna, y las 4 acertadas no coinciden (si coinciden seguimos)
    if set(conexiones_hz)!=set(marcadas):
        #Recogemos aquellas palabras que estan en la columna uno y no son aciertos
        for i in range(4):
            if conexiones_hz[i] not in marcadas:
                no_aciertos.append([conexiones_hz[i],i])
                
        # Permutamos estas palabras haciendo magia negra
        for i in range(4):
            for j in range(aciertos,4):
                word = grid_data[j*4+i]['text']
                if word in marcadas:
                    grid_data[j*4+i]['text']=no_aciertos[0][0]
                    grid_data[j*4+i]['color'] = '#f0ece4'
                    grid_data[j*4+i]['text_color'] = '#000000'
                    no_aciertos.remove(no_aciertos[0])

def game_over():
    global color
    flash("🐑 Beeeee 🐑")
    
    if color:
        colorines=[]
        for i in color:
            colorines.append(i["color"])
        if "#ffdc6c" not in colorines:
            color.append({"color":"#ffdc6c", "Tema": T_amarillo, "Texto": amarillo[0]+", "+amarillo[1]+", "+amarillo[2]+", "+amarillo[3]})
        if "#a0c45a" not in colorines:
            color.append({"color":"#a0c45a", "Tema": T_verde, "Texto": verde[0]+", "+verde[1]+", "+verde[2]+", "+verde[3]})
        if "#b1c4ef" not in colorines:
            color.append({"color":"#b1c4ef", "Tema": T_azul, "Texto": azul[0]+", "+azul[1]+", "+azul[2]+", "+azul[3]})
        if "#ba81c5" not in colorines:
            color.append({"color":"#ba81c5", "Tema": T_morado, "Texto": morado[0]+", "+morado[1]+", "+morado[2]+", "+morado[3]})
    else:
        color=[{"color":"#ffdc6c", "Tema": T_amarillo, "Texto": amarillo[0]+", "+amarillo[1]+", "+amarillo[2]+", "+amarillo[3]},          
            {"color":"#a0c45a", "Tema": T_verde, "Texto": verde[0]+", "+verde[1]+", "+verde[2]+", "+verde[3]},
            {"color":"#b1c4ef", "Tema": T_azul, "Texto": azul[0]+", "+azul[1]+", "+azul[2]+", "+azul[3]},
            {"color":"#ba81c5", "Tema": T_morado, "Texto": morado[0]+", "+morado[1]+", "+morado[2]+", "+morado[3]}]

def victoria():
    if num_lives==4:
        flash("🐐 Eres la CABRA! 🐐")
    elif num_lives==3: 
        flash("Enhorabuena!")
    elif num_lives==2:
        flash("Bastante bien")
    else:
        flash("Por los pelos...")

if __name__ == '__main__':
    app.run(debug=True)
