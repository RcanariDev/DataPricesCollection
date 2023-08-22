

import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import namedtuple

from siuba import _, arrange, select
from siuba import *
from siuba.dply.vector import n, row_number

#https://www.oechsle.pe/zapatillas/zapatillas-hombre

url = "https://www.oechsle.pe/zapatillas/zapatillas-hombre"
Articulo = namedtuple("Articulo", ["nombre", "precio_antes", "precio_actual", "descuento", "url_imagen"])
lista_articulos = []


r = requests.get(url)
html_contents = r.text

#Se trae todo el código HTML
html_soup = BeautifulSoup(html_contents, "html.parser")

articulos_mercado = html_soup.find_all("li", class_= "zapatillas-adidas-nike-y-mas-en-oferta-|-oechsle-pe")


for articulo in articulos_mercado:
    nombre = articulo.find("span", class_="text fz-15 fz-lg-17 prod-name").text
    try:
        precio_antes = articulo.find("span", class_="text text-gray-light text-del fz-11 fz-lg-13 ListPrice").text
        descuento = articulo.find("span", class_="flag-of ml-10").text
    except AttributeError:
        precio_antes = "N/A"
        descuento = "N/A"
    precio_actual = articulo.find("span", class_="text fz-lg-15 fw-bold BestPrice").text

    imagen = articulo.find("img")["src"]
    lista_articulos.append(Articulo(nombre, precio_antes, precio_actual, descuento, imagen))


lista_articulos


#Convertir la data a data frame
type(lista_articulos)
Data11 = pd.DataFrame(lista_articulos, columns=["nombre", "precio_antes", "precio_actual", "descuento", "url_imagen"])

Data11.dtypes

(
    Data11 >>
    arrange(_.precio_actual)
)


#Crear una variable "precio_antes1" que va a reemplazar los N/A
Data12 = (
    Data11 >>
    mutate(precio_antes1 = case_when(_,{
        _.precio_antes == "N/A" : _.precio_actual,
        True : _.precio_antes
    }))
)

#Reemplazar los puntos por vacios y poner solo un punto esta vez
#Para las variables: "precio_actual" y "precio_antes1"
Data12['precio_actual'] = Data12['precio_actual'].str.replace('S/. ', '')
Data12['precio_antes1'] = Data12['precio_antes1'].str.replace('S/. ', '')

#Data12['precio_actual'] = Data12['precio_actual'].str[:-3]+'.'+Data12['precio_actual'].str[-3:]
#Data12['precio_antes1'] = Data12['precio_antes1'].str[:-3]+'.'+Data12['precio_antes1'].str[-3:]

#Cambiar a float las variables: "precio_actual" y "precio_antes1"
Data12.dtypes
Data13 = Data12.astype({"precio_actual":float, "precio_antes1":float})
Data13.dtypes

#Crear la varibles "descuentoPor"
Data13['descuentoPor'] = Data13['descuento'].str.replace(' %', '')
Data13['descuentoPor'] = Data13['descuentoPor'].str.replace(',', '.')

#Reeemplazar los N/A por cero
#Crear una nueva variable que es la diferencia de precio
Data14 = (
    Data13 >>
    mutate(descuentoPor = case_when(_,{
        _.descuentoPor == "N/A" : 0,
        True : _.descuentoPor
    })) >>
    mutate(difPrecios = _.precio_antes1 - _.precio_actual)
)

#Convertir la variable "descuentoPor" a int
Data14.dtypes
Data15 = Data14.astype({"descuentoPor":float})
Data15.dtypes


#Realizar consultas
(
    Data15 >>
    arrange(-_.descuentoPor)
)


(
    Data15 >>
    arrange(-_.difPrecios)
)












