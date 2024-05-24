from calendar import day_name
import re

import geopandas as gpd
import fiona
import folium
from folium.plugins import GroupedLayerControl


file_path = r'spatial_files/Regular Routes.gpkg'

def sort_func(route_name):
    name_parts = re.search(
        r'(?P<day>\w+day)[A-Za-z~\s\(\)]+(?P<length>[\d\.]+)km', 
        route_name
    ).groupdict()

    return list(day_name).index(name_parts['day']),  float(name_parts['length'])

all_layers = dict()

for layer_name in fiona.listlayers(file_path):
    all_layers[layer_name] = gpd.read_file(file_path, layer=layer_name).to_crs(crs='EPSG:4326')

# Set up background layers, with "human-friendly" names
m = folium.Map(crs='EPSG3857', tiles=None)
folium.TileLayer('cartodb positron', name='Light Background').add_to(m)
folium.TileLayer('openstreetmap', name='Detailed Background', show=False).add_to(m)

feature_groups = []

for route_name in sorted(all_layers.keys(), key=sort_func):
    print(route_name)
    route_data = all_layers[route_name]
    
    fg = folium.FeatureGroup(name=route_name)
    folium.GeoJson(route_data).add_to(fg)

    first_point = route_data.geometry.iloc[0].coords[0][::-1]

    url = f'https://www.google.com/maps/@{",".join(map(str, first_point))},0a,75y,90t/data=!3m3!1e1!3m1!2e0'
    
    folium.Circle(
        first_point, radius=10, fill=True, fill_opacity=0.8, 
        popup=f'Start approximately (!!) <a href="{url}" target="_blank">here</a>'
    ).add_to(fg)

    m.add_child(fg)
    feature_groups.append(fg)

folium.LayerControl(collapsed=False).add_to(m)
layer_control = GroupedLayerControl(groups={'Regular Routes<br>(click start point for info)': feature_groups})
layer_control.add_to(m)

m.fit_bounds(m.get_bounds(), padding=(0, 0))
m.save('maps/index.html')
