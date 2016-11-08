import re
import hashlib
import markdown2
from bs4 import BeautifulSoup, Tag
from askbot.utils.html import urlize_html
from dj_web_rich_object.models import WebRichObject

URL_RE = re.compile(r"(https?://[^\"><\s]+)")


class Markdown(markdown2.Markdown):
    def preprocess(self, text):
        return text

    def postprocess(self, text):
        # Hack for unescape special chars
        for key, value in markdown2.g_escape_table.iteritems():
            text = text.replace(value, key)

        urls = set(URL_RE.findall(text))

        # Treat images as gallery
        post = BeautifulSoup(text, 'html.parser')
        imgs = post.find_all('img')

        gallery = Tag(name='div',
                      attrs={
                          'class': "gallery", 'style': 'display: none;',
                          'id': hashlib.md5(text.encode('utf-8')).hexdigest(),
                      })
        img_urls = [img['src'] for img in imgs]
        for img in imgs:
            img.extract()
            img.attrs.update({
                'data-image': img['src'],
                'data-description': img['alt'],
            })
            gallery.append(img)

        post.append(gallery)

        text = urlize_html(post.__unicode__())
        # Add url as web rich object
        wros = ''
        for url in urls:
            if url in img_urls:
                continue
            try:
                wro = WebRichObject.objects.create_or_update_from_url(url)
                if wro.type != 'image':
                    wros += wro.get_widget().content.decode('utf8')
                else:
                    img = Tag(name='img', attrs={
                        'alt': wro.description or '',
                        'src': wro.url,
                        'data-image': wro.url,
                        'data-description': wro.description or ''
                    })
                    gallery.append(img)
            except Exception as err:
               print err
               pass

        post.append(gallery)
        text = urlize_html(post.__unicode__())
        text += wros
        return text
