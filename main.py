import twitter
import requests
from PIL import Image
import io
import os
import sys
import time

def merge_images(images):
    im0, im1 = images

    imr0 = Image.new(im0.mode, (300, 900), 'white')
    r = im0.width / im0.height
    w, h = int(300 * (1 if r > 1 else r)), int(300 * (1/r if r > 1 else 1))
    if w % 2 == 1: w += 1
    if h % 2 == 1: h += 1
    x = (300 - w) // 2
    y = (300 - h) // 2
    imr0.paste(im0.resize((w, h)), (x, y, 300 - x, 300 - y))
    r = im1.width / im1.height
    w, h = int(300 * (1 if r > 1 else r)), int(300 * (1/r if r > 1 else 1))
    if w % 2 == 1: w += 1
    if h % 2 == 1: h += 1
    x = (300 - w) // 2
    y = (300 - h) // 2
    imr0.paste(im1.resize((w, h)), (x, 600 + y, 300 - x, 900 - y))

    imr1 = Image.new(im0.mode, (300, 900), 'white')
    r = im1.width / im1.height
    w, h = int(300 * (1 if r > 1 else r)), int(300 * (1/r if r > 1 else 1))
    if w % 2 == 1: w += 1
    if h % 2 == 1: h += 1
    x = (300 - w) // 2
    y = (300 - h) // 2
    imr1.paste(im1.resize((w, h)), (x, y, 300 - x, 300 - y))
    r = im0.width / im0.height
    w, h = int(300 * (1 if r > 1 else r)), int(300 * (1/r if r > 1 else 1))
    if w % 2 == 1: w += 1
    if h % 2 == 1: h += 1
    x = (300 - w) // 2
    y = (300 - h) // 2
    imr1.paste(im0.resize((w, h)), (x, 600 + y, 300 - x, 900 - y))
    return imr0, imr1


if __name__ == '__main__':
    if len(sys.argv) == 5:
        imr0, imr1 = merge_images([Image.open(sys.argv[1]).convert("RGBA"), Image.open(sys.argv[2]).convert("RGBA")])
        imr0.save(sys.argv[3])
        imr1.save(sys.argv[4])
    elif len(sys.argv) == 1:
        t = twitter.Api(
                consumer_key=os.getenv('API_KEY'),
                consumer_secret=os.getenv('API_SECRET_KEY'),
                access_token_key=os.getenv('ACCESS_TOKEN_KEY'),
                access_token_secret=os.getenv('ACCESS_TOKEN_SECRET'),
                sleep_on_rate_limit=True,
                )
        print(t.VerifyCredentials())
        since_id = None
        if os.path.exists('since_id'):
            with open('since_id', 'r') as fp:
                since_id = fp.read()
        while True:
            replies = t.GetMentions(since_id=since_id, count=1)
            if len(replies) == 0:
                print('sleeping')
                time.sleep(15)
                continue
            reply = replies[0]
            since_id = reply.id_str
            with open('since_id', 'w') as fp:
                fp.write(since_id)
            if not reply.media or len(reply.media) != 2:
                print('skipping reply')
                continue
            r0 = requests.get(reply.media[0].media_url_https)
            r1 = requests.get(reply.media[1].media_url_https)
            im0 = Image.open(io.BytesIO(r0.content)).convert("RGBA")
            im1 = Image.open(io.BytesIO(r1.content)).convert("RGBA")
            imr0, imr1 = merge_images([im0, im1])
            m0 = io.BytesIO()
            m0.name = '0.png'
            m0.mode = 'rb+'
            m1 = io.BytesIO()
            m1.name = '1.png'
            m1.mode = 'rb+'
            imr0.save(m0, 'PNG')
            imr1.save(m1, 'PNG')
            m0.seek(0)
            m1.seek(0)
            t.PostUpdate('', media=[m0, m1])
    else:
        sys.stderr.write(f'usage: {sys.argv[0]} [<src0> <src1> <dst0> <dst1>]')
        sys.exit(1)
