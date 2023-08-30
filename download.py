import csv
import os
import shutil
import time

import requests

# you can change this value if you want
dataset_folder_name = 'data'

if not os.path.exists(dataset_folder_name):
    os.makedirs(dataset_folder_name)


gallica_iiif_base_url = "https://gallica.bnf.fr/iiif/"
request_counter = 0

with open('./gallicalbum.csv', mode='r', encoding='utf-8') as fh:
    metadata = csv.reader(fh, delimiter=',')
    next(metadata)
    dataset = [link[0].replace('.item', '').replace('#', '') for link in metadata]

    # keeping that snippet of code in case of, format: [[ark, folio]]
    # dataset = [['/'.join(link[0].split('/')[3:6]), link[0].split('/')[6].replace('.item', '')]
            #    for link in metadata]

    for image in dataset:
        request_counter += 1
        image_name = '_'.join(image.split('/')[4:6])
        image_url = image + '/full/full/0/native.jpeg'

        r_image = requests.get(image_url, stream=True)
        if r_image.status_code == 200:
            print(f'Downloading {image_url}')
            with open(f'./{dataset_folder_name}/{image_name}.jpeg', 'wb') as f:
                shutil.copyfileobj(r_image.raw, f)
                #TODO: remove Gallica border at the bottom of the downloaded image
                print('Download complete!')
        
        if request_counter == 5:
            request_counter = 0
            # Apparently there is no need to limit requests to Gallica server at this time
            # time.sleep(62)


        # Keeping that snippet of code in case current method does not work because of permalinks
        '''if request_counter == 5:
            request_counter = 0
            print('time to sleep')
            time.sleep(62)'''

        """url = "https://gallica.bnf.fr/iiif/" + image[0] + "/manifest.json"
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