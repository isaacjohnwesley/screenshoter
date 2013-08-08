import os
from flask import Flask, request
from flask.ext import restful
from flask.ext.restful import reqparse
import random , string

import selenium.webdriver

import PIL
from PIL import Image
import base64
from io import BytesIO
import cStringIO

import boto
from boto.s3.key import Key

app = Flask(__name__)
api = restful.Api(app)
parser = reqparse.RequestParser()
parser.add_argument('url', type=str)

#AWS configurations
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
S3_BUCKET = ''

#Import secrets from the file the world should not see :P
try:
   from config import *
except ImportError:
   pass

conn = boto.connect_s3(config["AWS_ACCESS_KEY_ID"],config["AWS_SECRET_ACCESS_KEY"])

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

    #saving the image into a cStringIO object to avoid writing to disk
    out_img=cStringIO.StringIO()
    img.save(out_img,'PNG')

    return upload_to_s3(out_img)

def upload_to_s3(upload_img):
    try:
        bucket = conn.get_bucket(config["S3_BUCKET"])

        #generate an unique ID
        random_char = [random.choice(string.ascii_letters + string.digits) for n in xrange(12)]
        uniquid = "".join(random_char)

        k = bucket.new_key('screenshots/%s.png' % uniquid)
        k.set_contents_from_string(upload_img.getvalue(),headers={"Content-Type": "image/png"})
        k.make_public()
    except boto.exception.s3responseerror, e:
        raise
    finally:
        url=k.generate_url(expires_in=0 , query_auth=False)

    return url


api.add_resource(TakeScreenshot, '/takescreenshot')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug= True)