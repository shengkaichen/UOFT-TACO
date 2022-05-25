import io
from rest_framework.decorators import api_view
from django.http import HttpResponse
from . import utils
from . import visualize
from PIL import Image
from django.apps import apps

import numpy as np
import os
import matplotlib.pyplot as plt
import secrets

MODULE_DIR = os.path.dirname(__file__)  # get current directory
detectorConfig = apps.get_app_config("detector")
graph = detectorConfig.graph
config = detectorConfig.config
model = detectorConfig.model
class_map = detectorConfig.class_map

@api_view(["POST"])
def index(request):
    uuid = secrets.token_urlsafe(4)
    print("[TACO LOG] request start ( " + uuid + ' )')
    image = getImageFromRequest(request)
    print(np.shape(image))
    resultImage = detectImage(image, uuid)
    buf = io.BytesIO()
    resultImage.save(buf, format="JPEG")

    return HttpResponse(buf.getvalue(), content_type="image/jpeg" )
    # with open(os.path.join(MODULE_DIR, 'outputimgs', 'temp' + uuid +'.jpeg'), "rb") as f:
    #     return HttpResponse(f.read(), content_type="image/jpeg")

def getImageFromRequest(request):
    # get Image from request
    image = request.FILES.get("articleFiles[]")
    # transform the Image into nparray
    loadedImage = load_image(image)
    return loadedImage

def load_image(file):
    image = Image.open(file)
    img_shape = np.shape(image)

    # load metadata
    exif = image._getexif()
    if exif:
        exif = dict(exif.items())
        # Rotate portrait images if necessary (274 is the orientation tag code)
        if 274 in exif:
            if exif[274] == 3:
                image = image.rotate(180, expand=True)
            if exif[274] == 6:
                image = image.rotate(270, expand=True)
            if exif[274] == 8:
                image = image.rotate(90, expand=True)

    # If has an alpha channel, remove it for consistency
    if img_shape[-1] == 4:
        image = image[..., :3]

    return np.array(image)

def detectImage(image, uuid):
    global graph, config, model, class_map
    # Preperation
    plt.ioff()

    image_processed = preprocessImage(image, config)
    
    # Detection Starts
    with graph.as_default():
        r = model.detect([image_processed], verbose=0)[0]
    if r['class_ids'].shape[0]>0:
        r_fused = utils.fuse_instances(r)
    else:
        r_fused = r
    # print(r["scores"])
    # print(r_fused["scores"])
    keyArr = sorted(list(dict.fromkeys(class_map.values()))+ ["BG"])
    textLabelArr = []
    for class_id in r_fused['class_ids']:
        textLabelArr.append(keyArr[class_id])
        print("[TACO LOG] " + keyArr[class_id], " ",uuid)

    fig, ax2= plt.subplots(1, 1, figsize=(16, 16))

    visualize.display_instances(image_processed, r_fused['rois'], r_fused['masks'], r_fused['class_ids'],
        keyArr, r_fused['scores'], title="Predictions given by MRCNN", ax=ax2)
    
    fig.canvas.draw()

    # PIL Image
    return Image.frombytes('RGB', fig.canvas.get_width_height(),fig.canvas.tostring_rgb())
    # plt.savefig(os.path.join(MODULE_DIR, "outputimgs" ,'temp' + uuid +'.jpeg'))
    # plt.close()

def preprocessImage(image, config):
    image_processed, _1, _2, _3, _4 = utils.resize_image(
            image,
            min_dim=config.IMAGE_MIN_DIM,
            min_scale=config.IMAGE_MIN_SCALE,
            max_dim=config.IMAGE_MAX_DIM,
            mode=config.IMAGE_RESIZE_MODE)
    # mask = utils.resize_mask(mask, scale, padding, crop)
    return image_processed
