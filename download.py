import argparse
import csv
import os
import shutil
import time

import requests
import sys

parser = argparse.ArgumentParser(description='Download the Gallicalbum dataset.')
parser.add_argument('-low', action='store_true', help='Download the lower resolution version of the dataset. Default: high resolution')
args = parser.parse_args()

# create output folder
dataset_folder_name = 'data_test'
if not os.path.exists(dataset_folder_name):
    os.makedirs(dataset_folder_name)

# get URL to images from gallicalbum.csv
with open('./gallicalbum.csv', mode='r', encoding='utf-8') as fh:
    metadata = csv.reader(fh, delimiter=',')
    next(metadata)
    dataset = [link[0].replace('.item', '').replace('#', '') for link in metadata]

    # keeping that snippet of code in case of, format: [[ark, folio]]
    # dataset = [['/'.join(link[0].split('/')[3:6]), link[0].split('/')[6].replace('.item', '')]
            #    for link in metadata]

# download images
gallica_iiif_base_url = "https://gallica.bnf.fr/iiif"
cool_down = 59 # seconds
request_counter = 0

download_error = 0

if args.low:
    # we download the low resolution version
    for image in dataset:
        image_name = '_'.join(image.split('/')[4:7])
        image_url = image + '/full/full/0/native.jpeg'
        r_image = requests.get(image_url, stream=True)
        if r_image.status_code == 200:
            print(f'Downloading {image_url}')
            with open(f'./{dataset_folder_name}/{image_name}.jpg', 'wb') as f:
                shutil.copyfileobj(r_image.raw, f)
                #TODO: remove Gallica border at the bottom of the downloaded image 
            print('Download complete!')
        else:
            print(f'[E] Server reponse {r_image.status_code} on {image_url}')
            download_error += 1
else:
    # then we download the high resolution version
    # which confronts us to Gallica's traffic limitations
    for image_url in dataset[:6]:
        request_counter += 1

        chunks = image_url.split('/')
        ark_id = chunks[-3]
        doc_id = chunks[-2]
        folio = chunks[-1]
        iiif_url = f"{gallica_iiif_base_url}/ark:/{ark_id}/{doc_id}/{folio}/full/full/0/native.jpg"

        r_iiif = requests.get(iiif_url, stream=True)
        if r_iiif.status_code == 200:
            print(f'Downloading {iiif_url}')
            image_path = os.path.join(dataset_folder_name, f'{ark_id}_{doc_id}_{folio}.jpg')
            with open(image_path, 'wb') as f:
                shutil.copyfileobj(r_iiif.raw, f)
            print('Download complete!')
        else:
            print(f'[E] Server reponse {r_iiif.status_code} on {iiif_url}')
            download_error += 1
            
        if request_counter == 5:
            print("Cool down for 1 minute because of Gallica's traffic limitations.")
            for i in range(cool_down + 1):
                time.sleep(1)
                sys.stdout.write("\r" + f"{i * '█'}{(cool_down - i) * '░'}   {cool_down - i} second(s) left")
                sys.stdout.flush()
            print("\n")
            request_counter = 0

if download_error == 0:
    print("Gallicalbum dataset downloaded successfully!")
else:
    print("Dataset downloaded with errors. Please check the logs above ([E]).")
    print(f"{download_error}/{len(dataset)} images could not be downloaded.")
    print("In case of errors 429 from the server, you might want to increase the cool down time `download.py`.")


"""



    # Keeping that snippet of code in case current method does not work because of permalinks
    '''if request_counter == 5:
        request_counter = 0
        print('time to sleep')
        time.sleep(62)'''

    """"""url = "https://gallica.bnf.fr/iiif/" + image[0] + "/manifest.json"
    image_id = gallica_iiif_base_url + image [0] + '/canvas/' + image[1]

    r_manifest = requests.get(url)

    if r_manifest.status_code == 200:
        http_response = r_manifest.json()
        manifest_images = http_response['sequences'][0]['canvases']
        image_link = [link['images'][0]['resource']['@id']
                        for link in manifest_images if link['@id'] == image_id]
        
        print(image_link)
        
        r_image = requests.get(image_link[0])

        if r_image.status_code == 200:
            print('yes!')
        else:
            print(r_image.status_code)
    
    if request_counter == 5:
        request_counter = 0
        time.sleep(62)"""