import re, json, urllib.request

from flask import render_template, jsonify

from . import bp_api
from ..models.Foto import Foto


@bp_api.route('/iiif2/edh/<f_nr>.manifest.json', methods=['GET', 'POST'], strict_slashes=False)
def create_iiif_manifest(f_nr):
    """
    route for returning IIIF manifest file
    :param f_nr : F-No of image (string)
    :return: json IIIF manifest file
    """
    f_nr = re.sub(r'F0*?', r'', f_nr, flags=re.IGNORECASE)
    if re.match(r'^\d*$', f_nr):
        f_number = "{:06d}".format(int(f_nr))
        f_nr = "F" + "{:06d}".format(int(f_nr))
    results = Foto.query("f_nr:" + f_nr)
    if results['metadata']['number_of_hits'] == 0:
        return render_template('404.html'), 404
    else:
        # image size from IIIF info.json
        try:
            with urllib.request.urlopen("https://edh-www.adw.uni-heidelberg.de/iiif2/iiif/2/f"+f_number+".tif/info.json") as url:
                data = json.loads(url.read().decode())
                img_size_x = data['width']
                img_size_y = data['height']
        except:
            img_size_x = 0
            img_size_y = 0
        # create basic context of manifest
        iiif_dict = {'@context': "http://iiif.io/api/presentation/2/context.json",
                     '@id': "https://edh-www.adw.uni-heidelberg.de/iiif/edh/" + f_nr + ".manifest.json",
                     '@type': "sc:Manifest", 'label': "EDH Image",
                     'description': "Image(s) taken from the Epigraphic Database Heidelberg",
                     'license': "https://creativecommons.org/licenses/by-sa/4.0/",
                     'attribution': "Epigraphic Database Heidelberg (https://edh-www.adw.uni-heidelberg.de)"}
        # add metadata
        metadata = [{'label': 'Province / Italic region', 'value': results['items'][0].provinz},
                    {'label': 'Country', 'value': results['items'][0].land}]
        if results['items'][0].fo_antik:
            metadata.append({'label': 'Ancient find spot', 'value': results['items'][0].fo_antik})
        if results['items'][0].fo_modern:
            metadata.append({'label': 'Modern find spot', 'value': results['items'][0].fo_modern})
        if results['items'][0].aufbewahrung:
            metadata.append({'label': 'Present location', 'value': results['items'][0].aufbewahrung})
        iiif_dict['metadata'] = metadata
        # add sequence data
        sequence = [{'@type': 'sc:Sequence', 'label': 'EDH Sequence'}]
        # canvas data
        canvas = [{'@id': 'https://edh-www.adw.uni-heidelberg.de/digilib/edh/canvas/' + f_nr,# TODO: remove digilib specific URI
                   '@type': 'sc:Canvas',
                   'label': f_nr,
                   'height': img_size_y,
                   'width': img_size_x,
                   }]
        cv_metadata = [{'label': 'Foto ID', 'value': 'https://edh-www.adw.uni-heidelberg.de/edh/foto/' + f_nr}]
        if results['items'][0].aufschrift:
            cv_metadata.append({'label': 'Photo credits', 'value': results['items'][0].aufschrift})
        if results['items'][0].aufnahme_jahr:
            cv_metadata.append({'label': 'Date of photograph', 'value': results['items'][0].aufnahme_jahr})
        canvas[0]['metadata'] = cv_metadata
        cv_images = [{'@id': 'https://edh-www.adw.uni-heidelberg.de/digilib/edh/annotation/' + f_nr,
                      '@context': 'http://iiif.io/api/presentation/2/context.json',
                      '@type': 'oa:Annotation',
                      'motivation': 'sc:painting',
                      'on': 'https://edh-www.adw.uni-heidelberg.de/digilib/edh/canvas/' + f_nr.lower()
                      }]
        canvas[0]['images'] = cv_images
        resource = [{'@id': 'https://edh-www.adw.uni-heidelberg.de/digilib/Scaler/IIIF/' + f_nr.lower() + '.tif/full/full/0/default.png',# TODO: remove digilib specific URI
                     '@type': 'dctypes:Image',
                     'format': 'image/png',
                     'service': {
                         '@context': 'http://iiif.io/api/image/2/context.json',
                         '@id': 'https://edh-www.adw.uni-heidelberg.de/digilib/Scaler/IIIF/' + f_nr.lower() + '.tif', # TODO: remove digilib specific URI
                         'profile': 'http://iiif.io/api/image/2/level2.json',
                     }}]
        canvas[0]['images'][0]['resource'] = resource
        sequence[0]['canvases'] = canvas
        iiif_dict['sequences'] = sequence
        iiif_json = jsonify(iiif_dict)
        iiif_json.headers.add('Access-Control-Allow-Origin', '*')
        return iiif_json
