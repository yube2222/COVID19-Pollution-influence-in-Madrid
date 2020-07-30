# COVID-19 Confinement influence in pollution levels measured in Madrid

Project to evaluate if confinement performed at Comunidad de Madrid from March 15th to April 28th  affected pollution levels measured at 24 different Madrid locations.

## Project structure
## 1) Data: 
Data obtained from https://datos.madrid.es/. Processed and stored as .csv files, containing daily measured pollution levels at 24 different measure stations located in Comundad de Madrid.

path: **./data/**

## 2) Code:
The code loads whole available data, filter data from 2015 and performs:
- Fortnight average curve for pollution levels measured for years 2015 to 2019 (both included)
- Fortnight average curve for pollution levels measured during 2020 (January to June; both included)

Then, data is plotted using plotly library and stored as html.

script file: **./source/COVID19_Confinement_influence.py**

## 3) Output:
Resulting plotly plot stored as .html (ready to be open in web browser): 

**COVID19_POLLUTION_INFLUENCE_MADRID.html**


Screenshot of obtained plot as .png: 

**COVID19_POLLUTION_INFLUENCE_MADRID.png**