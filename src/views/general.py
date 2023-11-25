from flask import request, Blueprint, Response, jsonify, current_app
from src.dependencies import property_information
from PIL import Image
import folium
import io

general = Blueprint('general', __name__)

# basic health check
@general.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

#route to get lon and lat from uprn
@general.route('/lonlat', methods=['GET'])
def lonlat():
    uprn = request.args.get('uprn')
    lonlat = property_information.get_lon_lat_from_uprn(uprn)
    if lonlat is None:
        return Response(status=404)
    else:
        return jsonify(lonlat)

#route which returns property boundaries from uprn
@general.route('/property', methods=['GET'])
def property():
    # check for uprn or lon and lat
    uprn = request.args.get('uprn')
    lon = request.args.get('lon')
    lat = request.args.get('lat')
    
    if uprn is not None:
        lon_lat = property_information.get_lon_lat_from_uprn(uprn)
    elif lon is not None and lat is not None:
        uprn = "xxx" #TODO fix this
        lon_lat = {
            'lon': float(lon),
            'lat': float(lat)
        }
    else:
        return jsonify({'error': 'uprn or lon and lat is required'}), 400

    if lon_lat is None:
        return jsonify({'error': 'uprn not found'}), 404
    
    # get the boundaries from the property_information dependency
    boundaries = property_information.get_boundaries(lon_lat['lat'], lon_lat['lon'])
    if boundaries is None:
        return jsonify({'error': 'boundaries not found'}), 404
    
    # if hits is empty, return 404
    if len(boundaries['hits']['hits']) == 0:
        return jsonify({'error': 'boundaries not found'}), 404
    
    # get coordinates from the first hit
    coordinates = boundaries['hits']['hits'][0]['_source']['location']['coordinates'][0]
    inspire_id = boundaries['hits']['hits'][0]['_source']['inspireid']

    coordinates_string = ""
    for coordinate in coordinates:
        coordinates_string += "{},{}|".format(coordinate[1], coordinate[0])
    coordinates_string = coordinates_string[:-1]

    # check for listed buildings
    listed_buildings = property_information.get_listed_buildings(lon_lat['lat'], lon_lat['lon'])
    listed_buildings_found = False
    if listed_buildings is not None:
        if len(listed_buildings['hits']['hits']) > 0:
            listed_buildings_found = True
            listed_buildings_formatted = []
            for building in listed_buildings['hits']['hits']:
                listed_buildings_formatted.append({
                    'description': building['_source']['name'],
                    'list_date': building['_source']['list_date'],
                    'grade': building['_source']['grade'],
                    'link': building['_source']['link']
                })
    
    # check for historical floods
    historical_floods = property_information.get_historicalfloods(lon_lat['lat'], lon_lat['lon'])
    historical_floods_found = False
    if historical_floods is not None:
        if len(historical_floods['hits']['hits']) > 0:
            historical_floods_found = True
            historical_floods_formatted = []
            for flood in historical_floods['hits']['hits']:
                historical_floods_formatted.append({
                    'geometry': flood['_source']['polygon'],
                    'area': flood['_source']['area'],
                    'perimeter': flood['_source']['perimeter']
                })

    # get fire and rescue authority
    fire_and_rescue_authority = property_information.get_fire_and_rescue_authority(lon_lat['lat'], lon_lat['lon'])
    fire_and_rescue_authority_data = None
    fire_and_rescue_uk_data = property_information.get_fire_and_rescue_data("uk_total")
    if fire_and_rescue_authority is not "Not found":
        fire_and_rescue_authority_data = property_information.get_fire_and_rescue_data(fire_and_rescue_authority)
    
    output = {
        'inspire_id': inspire_id,
        'map_url': "https://maps.googleapis.com/maps/api/staticmap?ex25sg&zoom=19&size=2000x1000&key=AIzaSyCkRmFd70025GGwj78YhA3PCw6f9AMjfOQ&maptype=satellite&path={}".format(coordinates_string),
        'listed_buildings_found_within_500m': listed_buildings_found,
        'fire_and_rescue_authority': fire_and_rescue_authority,
        'fire_and_rescue_uk_data': fire_and_rescue_uk_data,
    }

    if listed_buildings_found:
        output['listed_buildings'] = listed_buildings_formatted

    if historical_floods_found:
        print(historical_floods_found)
        output['historical_floods'] = historical_floods_formatted
        new_map = create_map(lon_lat, historical_floods_formatted)
        output['historical_floods_image'] = create_image(new_map)



    if fire_and_rescue_authority_data is not None:
        output['fire_and_rescue_authority_data'] = fire_and_rescue_authority_data



    return jsonify(output)

    #https://maps.googleapis.com/maps/api/staticmap?center=1,badger%20close,ex25sg&zoom=19&size=2000x1000&key=AIzaSyCkRmFd70025GGwj78YhA3PCw6f9AMjfOQ&maptype=satellite&path=50.720667261903266,-3.480217239090186|50.72060758281267,-3.480362978324894|50.72047539913977,-3.480134689332379|50.72046308297075,-3.480113050633926|50.720459136402674,-3.480105134393619|50.720457392361745,-3.48010082932502|50.720456106807305,-3.480095830358837|50.72045483923362,%20-3.480089415261003|50.72045400317479,-3.480084430463352|50.720453625602296,-3.480078751767846|50.72045378742945,-3.480066006580798|50.72045431783865,-3.480059648154964|50.720455288753385,-3.480054011962633|50.72045626865811,-3.480047667704075|50.72045768906845,-3.480042045678832|50.72047743328863,-3.479993607694928|50.72047056264925,-3.479984366774174|50.72049613896191,-3.479917879634037|50.72054882703313,-3.479830429645301|50.72060000833523,-3.479741231939771|50.72074305209687,-3.479942279432938|50.720667261903266,-3.480217239090186

def create_map(lon_lat, historical_floods_formatted):
    # Set the center location and zoom level
    zoom_level = 10

    # Create the folium map object
    map = folium.Map(location=[lon_lat['lat'], lon_lat['lon']], zoom_start=zoom_level)
    for hit in historical_floods_formatted:
        flood_data = hit['geometry']
        polygon_coordinates = flood_data['polygon']['coordinates'][0]
        folium.Polygon(locations=polygon_coordinates, color='red', fill=True, fill_color='red').add_to(map)

def create_image(map):
    # Create an in-memory file object
    img_data = io.BytesIO()

    # Save the folium map as an image in the file object
    map.save(img_data, format='PNG')

    # Rewind the file object to the beginning
    img_data.seek(0)
    image=Image.open(img_data)
    image.save('/opt/src/views/historicalfloods.png', 'PNG')

    # Open the image with PIL
    return Image.open(img_data)