import geopandas as gpd
import fiona
import folium
from folium.plugins import GroupedLayerControl


file_path = r'spatial_files/Regular Routes.gpkg'

all_layers = dict()

for layer_name in fiona.listlayers(file_path):
    all_layers[layer_name] = gpd.read_file(file_path, layer=layer_name).to_crs(crs='EPSG:4326')

m = folium.Map(tiles='cartodb positron', crs='EPSG3857')

feature_groups = []

for route_name, route_data in all_layers.items():
    print(route_name)
    
    fg = folium.FeatureGroup(name=route_name)
    folium.GeoJson(route_data).add_to(fg)

    first_point = route_data.geometry.iloc[0].coords[0][::-1]

    url = f'https://www.google.com/maps/@{",".join(map(str, first_point))},0a,75y,90t/data=!3m3!1e1!3m1!2e0'
    
    folium.Circle(first_point, radius=10, fill=True, fill_opacity=0.8, popup=f'Start approximately (!!) <a href="{url}" target="_blank">Here</a>').add_to(fg)
    
    m.add_child(fg)
    feature_groups.append(fg)

layer_control = GroupedLayerControl(groups={'Regular Routes': feature_groups}, collapsed=False)
layer_control.add_to(m)

m.fit_bounds(m.get_bounds(), padding=(0, 0))
m.save('site/index.html')
