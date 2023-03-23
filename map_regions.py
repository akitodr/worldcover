from os import sep
from PIL import Image
from utils import read_from_file, xiaoline
from haversine import haversine
import json
import easygui

Image.MAX_IMAGE_PIXELS = 1000000000000000000

RANGE = 6
START_X = -54
START_Y = -21

END_X = START_X + RANGE
END_Y = START_Y - RANGE

color_mapping = {
    "tree_cover": (0, 100, 0),
    "shrubland": (255, 187, 34),
    "grassland": (255, 255, 76),
    "cropland": (240, 150, 255),
    "built-up": (250, 0, 0),
    "sparse_veg": (180, 180, 180),
    "snow_ice": (240, 240, 240),
    "water": (0, 100, 200),
    "herbaceous": (0, 150, 160),
    "mangroves": (0, 207, 117),
    "moss_lichen": (250, 230, 160)
}

def get_pixel_coords_from_latlon(lat, lon, width, height):
    x = (lon - START_X) / RANGE * width
    y = (START_Y - lat) / RANGE * height

    return (x, y)

def get_pixels_between_coords(img, lat1, lon1, lat2, lon2):
    if lat1 > START_Y or lat1 < END_Y or lat2 > START_Y or lat2 < END_Y or lon1 < START_X or lon1 > END_X or lon2 < START_X or lon2 > END_X:
        raise Exception("Parameters out of bounds") 

    width, height = img.size
    x0, y0 = get_pixel_coords_from_latlon(lat1, lon1, width, height)
    x1, y1 = get_pixel_coords_from_latlon(lat2, lon2, width, height)

    coords = xiaoline(x0, y0, x1, y1)
    pixels = [img.getpixel(coord) for coord in coords]

    return pixels

# def cropImage(lat1, lon1, lat2, lon2):
#     crop_img = img.crop((lon1, lat1, lon2, lat2))
#     return crop_img

def compare_pixel_colors(pixel):
    if(pixel == color_mapping["tree_cover"]):
        return "árvores"
    elif(pixel == color_mapping["shrubland"]):
        return "arbustos"
    elif(pixel == color_mapping["grassland"]):
        return "pasto"
    elif(pixel == color_mapping["cropland"]):
        return "plantação"
    elif(pixel == color_mapping["built-up"]):
        return "construção"
    elif(pixel == color_mapping["sparse_veg"]):
        return "vegetação esparsa"
    elif(pixel == color_mapping["snow_ice"]):
        return "neve/gelo"
    elif(pixel == color_mapping["water"]):
        return "água"
    elif(pixel == color_mapping["herbaceous"]):
        return "herbáceos"
    elif(pixel == color_mapping["mangroves"]):
        return "mangues"
    elif(pixel == color_mapping["moss_lichen"]):
        return "musgos"

def create_dict_from_csv(df):
    coords = []
    for index, rows in df.iterrows():
        info = {
            'origem': rows['ORIGEM'],
            'destino': rows['DESTINO'],
            'lat_origem': rows['LATITUDE ORIGEM'],
            'lon_origem': rows['LONGITUDE ORIGEM'],
            'lat_destino': rows['LATITUDE DESTINO'],
            'lon_destino': rows['LONGITUDE DESTINO'],
        }
        coords.append(info)

    return coords

def create_dict(name_org, name_dest, lat_org, lon_org, lat_dest, lon_dest):
    info = {
        'origem': name_org,
        'destino': name_dest,
        'lat_origem': lat_org,
        'lon_origem': lon_org,
        'lat_destino': lat_dest,
        'lon_destino': lon_dest,
    }

    return info

def classify_regions_between_link():
    path = easygui.fileopenbox()
    names = path.split(sep='\\')
    names = names[-1].split(sep='.')

    img_path = './parana/converted/'
    img = Image.open(img_path + 'parana_complete.png')

    file_name = ''
    df = read_from_file(path)

    coords_list = create_dict_from_csv(df)

    for info in coords_list:
        pixels = []
        result = []
        reg = []
        
        current_item = ''
        current_count = 0       
        
        lat1 = info['lat_origem']
        lon1 = info['lon_origem']
        lat2 = info['lat_destino']
        lon2 = info['lon_destino']

        link_org = (lat1, lon1)
        link_dest = (lat2, lon2)
        distance = haversine(link_org, link_dest) * 1000
        info['distance(meters)'] = distance

        pixels = get_pixels_between_coords(img, lat1, lon1, lat2, lon2)
        for pixel in pixels:
            reg.append(compare_pixel_colors(pixel))

        for item in reg:
            if item != current_item and current_item != '':
                percentage = current_count / len(reg)
                result.append({
                    f'{current_item}_percentage': percentage,
                    f'{current_item}_distance': distance * percentage
                })
                current_count = 0
            current_count += 1
            current_item = item

        percentage = current_count / len(reg)
        result.append({
            f'{current_item}_percentage': percentage,
            f'{current_item}_distance': distance * percentage
        })
        info['regions'] = result

    json_object = json.dumps(coords_list, indent = 2, ensure_ascii=False)
    print('done!')
    with open(f'./parana/coords/{names[-2]}.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json_object)


def classify_regions_by_coordinates(name_org, name_dest, lat_org, lon_org, lat_dest, lon_dest):
    region = []
    result = []

    current_item = ''
    current_count = 0  

    img_path = './parana/converted/'
    img = Image.open(img_path + 'parana_complete.png')
    
    coords_dict = create_dict(name_org, name_dest, lat_org, lon_org, lat_dest, lon_dest)

    link_org = (lat_org, lon_org)
    link_dest = (lat_dest, lon_dest)
    distance = haversine(link_org, link_dest) * 1000
    print(distance)

    pixels = get_pixels_between_coords(img, lat_org, lon_org, lat_dest, lon_dest)
    for pixel in pixels:
        region.append(compare_pixel_colors(pixel))

    for item in region:
            if item != current_item and current_item != '':
                percentage = current_count / len(region)
                result.append({
                    f'{current_item}_percentage': percentage,
                    f'{current_item}_distance': distance * percentage
                })
                current_count = 0
            current_count += 1
            current_item = item

    coords_dict['distance (meters)'] = distance
    coords_dict['regions'] = result
    json_result = json.dumps(coords_dict, indent = 2, ensure_ascii=False)
    print(json_result)
    

classify_regions_by_coordinates("GE064", "S-A-001", -26.14818, -53.02522, -26.149718677384, -53.018981962476)