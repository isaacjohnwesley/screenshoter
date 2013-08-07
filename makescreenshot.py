import os
from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse

import selenium.webdriver

import PIL
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
api = restful.Api(app)
parser = reqparse.RequestParser()
parser.add_argument('url', type=str)

class TakeScreenshot(restful.Resource):
    def get(self):
        return {'hello': 'get'}

    def post(self):
        args = parser.parse_args()
        finalink=take_screenshot('http://%s' %(args['url']))
        return finalink


def take_screenshot(url):
    try:
        webdriver = selenium.webdriver.PhantomJS()
        webdriver.get(url)
        webdriver.set_window_size(1280,800)
        imagedata = webdriver.get_screenshot_as_base64()
    finally:
        webdriver.close()
        webdriver.quit()

    return process_screenshot(imagedata)

def process_screenshot(base64_img):
    basewidth = 220
    img = Image.open(BytesIO(base64.b64decode(base64_img)))
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
    img = img.crop((0,0,basewidth,basewidth))
    img.save('isaac.png')

    finalurl="www.amazon.bucket.url-id-link.png"

    return finalurl


api.add_resource(TakeScreenshot, '/takescreenshot')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug= True)