import re
import random
import time
import json
import tabula
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from selenium import webdriver
from sklearn.neighbors import KernelDensity
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

with open(f'clasificated_ranking.json', 'r') as f:
    ranking = json.load(f)
    

def clear_data(data):
    for key in data:
        for registro in data[key]:
            for i in [2, 3, 4, 5]:
                if registro[i] != "":
                    registro[i] = registro[i][:-6]
    return data

with open('data.json', 'r') as f:
            dataf = json.load(f)
data = clear_data(dataf)

def pocos_enfrentamientos(team1, team2, event):
    
    conteos = {}
    for team3 in data:
        if team3 in [team1, team2]: continue
        enfrentamientos1, wins1 = stats(team1, team3, event, False)
        if enfrentamientos1 == 0: continue
        enfrentamientos2, wins2 = stats(team3, team2, event, False)
        if enfrentamientos2 == 0: continue
        
        conteos[team3] = (enfrentamientos1, enfrentamientos2, wins1, wins2)
        
    # Encontrar el atleta con la menor diferencia de enfrentamientos
    atleta_c = None
    mayor_num = -float('inf')
    wins_team1 = 0
    total_enfrentamientos = 0
    for atleta, (enfrentamientos1, enfrentamientos2, wins1, wins2) in conteos.items():
        num = (enfrentamientos1 + enfrentamientos2) / (abs(enfrentamientos1 - enfrentamientos2) + 1)
        if num > mayor_num:
            mayor_num = num
            atleta_c = atleta
            wins_team1 = wins1 + wins2
            total_enfrentamientos = enfrentamientos1 + enfrentamientos2
        elif num == mayor_num:
            if total_enfrentamientos < enfrentamientos1 + enfrentamientos2:
                mayor_num = num
                atleta_c = atleta
                wins_team1 = wins1 + wins2
                total_enfrentamientos = enfrentamientos1 + enfrentamientos2
    return (total_enfrentamientos, wins_team1) if atleta_c else (0, 0)

def define_winner(enfrentamientos, victorias_team1, team1, team2):
    if enfrentamientos == 0:
        try:
            rankTeam1 = ranking[team1]
            rankTeam2 = ranking[team2]
            if rankTeam1 < rankTeam2: return team1 
            else: return team2
        except:
            try:
                rankTeam1 = ranking[team1[0]] + ranking[team1[1]] + ranking[team1[2]]
                rankTeam2 = ranking[team2[0]] + ranking[team2[1]] + ranking[team2[2]]
                if rankTeam1 < rankTeam2: return team1 
                else: return team2
            except:
                rankTeam1 = ranking[team1[0]] + ranking[team1[1]]
                rankTeam2 = ranking[team2[0]] + ranking[team2[1]]
                if rankTeam1 < rankTeam2: return team1 
                else: return team2
    else:
        winner1_prob = victorias_team1 / enfrentamientos
    
    numero_aleatorio = random.uniform(0, 1)
    
    if numero_aleatorio < winner1_prob:
        return team1
    else: 
        return team2
    
def stats(team1, team2, event=None, rebuscar=True):
    
    enfrentamientos = 0
    victorias_team1 = 0
    
    if event == "S":
        # Verificar si los jugadores existen en el data
        if team1 in data and team2 in data:
            # Iterar sobre los registros de team1
            for registro in data[team1]:
                # Asegurarse de que el registro tiene la longitud adecuada y contiene nombres de jugadores
                if len(registro) > 11 and (team1 in registro or team2 in registro):
                    # Contar enfrentamiento si ambos jugadores están presentes
                    if team1 in registro and team2 in registro:
                        enfrentamientos += 1
                        # Contar victoria para team1
                        if registro[11] == team1 or registro[12] == team1:
                            victorias_team1 += 1
    elif event == "M":
        # Verificar si los jugadores existen en el data
        if team1[0] in data and team2[0] in data and team1[1] in data and team2[1] in data:
            # Iterar sobre los registros de team1
            for registro in data[team1[0]]:
                # Asegurarse de que el registro tiene la longitud adecuada y contiene nombres de jugadores
                if len(registro) > 11 and (team1[0] in registro and team1[1] in registro and team2[0] in registro and team2[1] in registro):
                    enfrentamientos += 1
                    # Contar victoria para team1
                    if (registro[11] == team1[0] and registro[12] == team1[1]) or (registro[11] == team1[1] and registro[12] == team1[0]):
                        victorias_team1 += 1        
                        
    if rebuscar and enfrentamientos < 1:
        (x, y) = pocos_enfrentamientos(team1, team2, event)
        enfrentamientos = x
        victorias_team1 = y
    return enfrentamientos, victorias_team1
    
def enfrentamiento(team1, team2, event):
    if event == "T":
        # Por equipos: de 5 a ganar 3, cada equipo es de 3 jugadores (ABC vs XYZ)
        #     Doble B+C vs Y+Z
        #     Individual A vs X
        #     Individual C vs Z
        #     Individual A vs Y
        #     Individual B vs X
        
        vt1 = 0
        vt2 = 0
        
        enfrentamientos, victorias_team1 = stats((team1[1], team1[2]), (team2[1], team2[2]), event)
        winner1 = define_winner(enfrentamientos, victorias_team1, team1, team2)
        if winner1 == team1: vt1 += 1 
        else: vt2 +=1
        
        enfrentamientos, victorias_team1 = stats(team1[0], team2[0], event)
        winner2 = define_winner(enfrentamientos, victorias_team1, team1, team2)
        if winner2 == team1: vt1 += 1 
        else: vt2 +=1
        
        enfrentamientos, victorias_team1 = stats(team1[2], team2[2], event)
        winner3 = define_winner(enfrentamientos, victorias_team1, team1, team2)
        if winner3 == team1: vt1 += 1 
        else: vt2 +=1
        
        if vt1 > 2:
            return winner1
        elif vt2 > 2:
            return winner1
        else:
            enfrentamientos, victorias_team1 = stats(team1[0], team2[1], event)
            winner4 = define_winner(enfrentamientos, victorias_team1, team1, team2)
            if winner4 == team1: vt1 += 1 
            else: vt2 +=1
            
            if vt1 > 2:
                return winner4
            elif vt2 > 2:
                return winner4
            else:
                enfrentamientos, victorias_team1 = stats(team1[1], team2[0], event)
                return define_winner(enfrentamientos, victorias_team1, team1, team2)
    
    else:
        enfrentamientos, victorias_team1 = stats(team1, team2, event)
        return define_winner(enfrentamientos, victorias_team1, team1, team2)
    
def FirstRoundsInd(homeclubs, aways):
    winners = []
    for i in range(16):
        team1 = random.choice(homeclubs)
        homeclubs.remove(team1)
        if aways:
            team2 = random.choice(aways)
            aways.remove(team2)
            winners.append(enfrentamiento(team1, team2, "S"))
        else:
            winners.append(team1)
    return winners

def BracketInd(homes, aways):
    number1 = homes[0]
    number2 = homes[1]
    number3to4 = homes[2:4]
    number5to8 = homes[4:9]
    number9to16 = homes[8:]
    
    # Round of 32
    team1 = number1
    team2 = random.choice(aways)
    aways.remove(team2)
    winner1 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner2 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner3 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number5to8)
    number5to8.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner4 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number5to8)
    number5to8.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner5 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner6 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner7 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number3to4)
    number3to4.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner8 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number3to4)
    number3to4.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner9 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner10 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner11 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number5to8)
    number5to8.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner12 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number5to8)
    number5to8.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner13 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner14 = enfrentamiento(team1, team2, "S")
    
    team1 = random.choice(number9to16)
    number9to16.remove(team1)
    team2 = random.choice(aways)
    aways.remove(team2)
    winner15 = enfrentamiento(team1, team2, "S")
    
    team1 = number2
    team2 = random.choice(aways)
    aways.remove(team2)
    winner16 = enfrentamiento(team1, team2, "S")
    
    winners = [winner1, winner2, winner3, winner4, winner5, winner6, winner7, winner8, winner9, winner10, winner11, winner12, winner13, winner14, winner15, winner16]
    
    return Final16(winners, "S")

def choose(array):
    element = random.choice(array)
    array.remove(element)
    return element

def Final16(winners, event):
    if event == "S":
        number1 = winners[0]
        number2 = winners[1]
        number3to4 = winners[2:4]
        number5to8 = winners[4:9]
        number9to16 = winners[8:]
        
        winners = ["empty", number1, choose(number9to16), choose(number9to16), choose(number5to8), choose(number5to8), 
                    choose(number9to16), choose(number9to16), choose(number3to4), choose(number3to4), choose(number9to16), 
                    choose(number9to16), choose(number5to8), choose(number5to8), choose(number9to16), choose(number9to16), number2]
        
    
    # Round of 16
    winner1R16 = enfrentamiento(winners[1], winners[2], event)
    winner2R16 = enfrentamiento(winners[3], winners[4], event)
    winner3R16 = enfrentamiento(winners[5], winners[6], event)
    winner4R16 = enfrentamiento(winners[7], winners[8], event)
    winner5R16 = enfrentamiento(winners[9], winners[10], event)
    winner6R16 = enfrentamiento(winners[11], winners[12], event)
    winner7R16 = enfrentamiento(winners[13], winners[14], event)
    winner8R16 = enfrentamiento(winners[15], winners[16], event)
    
    top8 = [winner1R16, winner2R16, winner3R16, winner4R16, winner5R16, winner6R16, winner7R16, winner8R16]
    
    # Quarterfinals
    winner1QF = enfrentamiento(winner1R16, winner2R16, event)
    top8.remove(winner1QF)
    top8.insert(0, winner1QF)
    
    winner2QF = enfrentamiento(winner3R16, winner4R16, event)
    top8.remove(winner2QF)
    top8.insert(0, winner2QF)
    
    winner3QF = enfrentamiento(winner5R16, winner6R16, event)
    top8.remove(winner3QF)
    top8.insert(0, winner3QF)
    
    winner4QF = enfrentamiento(winner7R16, winner8R16, event)
    top8.remove(winner4QF)
    top8.insert(0, winner4QF)
    
    # Semifinals
    winner1SF = enfrentamiento(winner1QF, winner2QF, event)
    top8.remove(winner1SF)
    top8.insert(0, winner1SF)
    
    winner2SF = enfrentamiento(winner3QF, winner4QF, event)
    top8.remove(winner2SF)
    top8.insert(0, winner2SF)
    
    # Final
    FinalWinner = enfrentamiento(winner1SF, winner2SF, event)
    top8.remove(FinalWinner)
    top8.insert(0, FinalWinner)
    
    return top8

def singles(genre):
    
    with open(f'single{genre}.json', 'r') as f:
        data1 = json.load(f)
    with open(f'clasificated_ranking.json', 'r') as f:
        info = json.load(f)
    datos = {}
    for name in data1:
        datos[name] = info[name]
        
    diccionario_ordenado = dict(sorted(datos.items(), key=lambda item: item[1]))
    
    datos = list(diccionario_ordenado.keys())
    
    aways16 = FirstRoundsInd(datos[16:32], FirstRoundsInd(datos[32:48], FirstRoundsInd(datos[48:64], datos[64:])))
    
    return BracketInd(datos[:16], aways16)

def teams(genre):
    with open(f'teams{genre}.json', 'r') as f:
        data = json.load(f)
    with open(f'clasificated_ranking.json', 'r') as f:
        info = json.load(f)
    
    info_tupla = list(zip(data[::3], data[1::3], data[2::3]))
    datos = {}
    # Corregimos el bucle para sumar los valores de ranking de cada nombre en la tupla
    for name in info_tupla:
        # Sumamos los valores de ranking para cada nombre en la tupla
        datos[name] = sum(info[nombre] for nombre in name if nombre in info)
        
    diccionario_ordenado = dict(sorted(datos.items(), key=lambda item: item[1]))
    
    datos = ["empty"] + list(diccionario_ordenado.keys())

    return Final16(datos[:17], "T")

def mixed():
    with open(f'mixedM.json', 'r') as f:
        mixedM = json.load(f)
    with open(f'mixedW.json', 'r') as f:
        mixedW = json.load(f)
        
    tuplas_mixed = [(nombreM, nombreW) for nombreM, nocM in mixedM.items() for nombreW, nocW in mixedW.items() if nocM == nocW]
    
    with open(f'clasificated_ranking.json', 'r') as f:
        info = json.load(f)
    
    datos = {}
    # Corregimos el bucle para sumar los valores de ranking de cada nombre en la tupla
    for name in tuplas_mixed:
        # Sumamos los valores de ranking para cada nombre en la tupla
        datos[name] = sum(info[nombre] for nombre in name if nombre in info)
        
    diccionario_ordenado = dict(sorted(datos.items(), key=lambda item: item[1]))
    
    datos = ["empty"] + list(diccionario_ordenado.keys())

    return Final16(datos[:17], "M")

def simulate(modalidad):
    # Inicializar un diccionario para almacenar los conteos
    conteos = {i: {} for i in range(1, 9)}
    
    # Ejecutar Knockout_stage 10000 veces
    for _ in range(1000):
        if modalidad == "SM":
            result = singles("Men")
        elif modalidad == "SW":
            result = singles("Women")
        elif modalidad == "TM":
            result = teams("Men")
        elif modalidad == "TW":
            result = teams("Women")
        elif modalidad == "M":
            result = mixed()
        else:
            raise Exception(f"no existe la modalidad {modalidad}")
        # Contar cuántas veces cada equipo aparece en cada posición
        for i, equipo in enumerate(result, start=1):
            if equipo in conteos[i]:
                conteos[i][equipo] += 1
            else:
                conteos[i][equipo] = 1

    # Convertir los conteos a un DataFrame
    tabla_promedio = pd.DataFrame(conteos)
    
    # Definir los pesos para cada posición
    pesos = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}

    # Multiplicar los conteos de cada posición por su peso correspondiente
    tabla_ponderada = tabla_promedio.mul([pesos[i] for i in range(1, 9)], axis=1)

    # Sumar los conteos ponderados para cada equipo
    totales_ponderados = tabla_ponderada.sum(axis=1)
    
    # Ordenar los equipos por el total ponderado
    totales_ponderados_ordenados = totales_ponderados.sort_values(ascending=False)

    # Crear un nuevo DataFrame con los resultados
    tabla_final_ponderada = pd.DataFrame({'Equipo': totales_ponderados_ordenados.index, 'Total ponderado': totales_ponderados_ordenados.values})
    
    # Imprimir la tabla final ponderada
    return tabla_final_ponderada['Equipo'][:8]

print(simulate("SM"))
print(simulate("SW"))
print(simulate("TM"))
print(simulate("TW"))
print(simulate("M"))

