import pandas as pd
import folium
import math
import sys
import io
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

MAP_POINT = [-104.83436325, 41.312958]
VIEW_TYPE = 'cartodbpositron'
ZOOM_START = 5
PATH_TO_LOAD_FILE = 'csv/worldcities.csv'
PATH_TO_SAVE_FILE = 'csv/paths.csv'

df = pd.read_csv(
     PATH_TO_LOAD_FILE
)

filtered_df = df[['city_ascii', 'lat', 'lng', 'iso3', 'admin_name', 'id']]
filtered_df = filtered_df[filtered_df['iso3'] == 'USA']
filtered_df = filtered_df[filtered_df['admin_name'] == 'Illinois']
filtered_df = filtered_df.head(10)

map = folium.Map(location=list(reversed(MAP_POINT)), tiles=VIEW_TYPE, zoom_start=ZOOM_START)
for coord in filtered_df.itertuples():
    folium.Marker(location=list(reversed([coord.lng, coord.lat]))).add_to(map)

dfToLook1 = filtered_df[['lat', 'lng', 'id']]
dfToLook2 = filtered_df[['lat', 'lng', 'id']]
data_types = {'city1Id': 'int64', 'city2Id': 'int64', 'distance': 'float'}
paths = pd.DataFrame(columns=data_types.keys()).astype(data_types)

print("Calculating paths")
for element1Tuple in dfToLook1.iterrows():
    element1 = element1Tuple[1]
    # TODO usunac samego siebie
    dfToLook2 = dfToLook2[dfToLook2['id'] != element1Tuple[1]['id']]
    for element2Tuple in dfToLook2.iterrows():
        element2 = element2Tuple[1]
        oneCity = [element1['lat'], element1['lng']]
        secondCity = [element2['lat'], element2['lng']]
        distance = math.dist(oneCity, secondCity)
        recordValues = {'city1Id':  element1['id'], 'city2Id':  element2['id'], 'distance': distance}
        record = pd.DataFrame([recordValues]).astype(data_types)
        paths = pd.concat([paths, record], ignore_index=True)
        print(record)

print(type(paths))
pathsShuffled = paths.sample(frac=1)
paths = pathsShuffled.head(30)

print("Printing paths")
i = 0
for pathTuple in paths.iterrows():
    # if i < 2000: # 200k max
        path = pathTuple[1]
        coordCity1 = (filtered_df[filtered_df['id'] == path['city1Id']][['lat']].values.flatten()[0], filtered_df[filtered_df['id'] == path['city1Id']][['lng']].values.flatten()[0])
        coordCity2 = (filtered_df[filtered_df['id'] == path['city2Id']][['lat']].values.flatten()[0], filtered_df[filtered_df['id'] == path['city2Id']][['lng']].values.flatten()[0])
        print(coordCity1)
        folium.PolyLine(locations=[coordCity1, coordCity2], color='green').add_to(map)
    # i+=1

paths.to_csv(PATH_TO_SAVE_FILE, index=False, sep=';')

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Map')
        self.window_width, self.window_height = 1700, 1000
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        data = io.BytesIO() 
        map.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        layout.addWidget(webView)


app = QApplication(sys.argv)
app.setStyleSheet('QWidget {font-size: 35px;}')

window = Window()
window.show()

try:
    sys.exit(app.exec_())
except SystemExit:
    print('Closing Window...')