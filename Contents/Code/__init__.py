
import re
import urllib

# We try and exclusively query google to avoid thrashing animemusicvideos.org
GOOGLE_JSON_AMVS = 'http://ajax.googleapis.com/ajax/services/search/web'\
    '?v=1.0&rsz=large&q="site:animemusicvideos.org"+video+information+%s'

AMV_INFO_URL = 'http://www.animemusicvideos.org/popups/vid_info.php?v=%s'
AMV_FULL_URL = 'http://www.animemusicvideos.org/members/'\
    'members_videoinfo.php?v=%s'


def Start():
    pass


class AMVAgent(Agent.Movies):
    name = 'Anime Music Videos'
    languages = [Locale.Language.English]

    def search(self, results, media, lang, manual):
        sanitized_name = media.name.lower()
        if sanitized_name.startswith('amv'):
            sanitized_name = sanitized_name[3:]
        sanitized_name = sanitized_name.replace('-', ' ')
        sanitized_name = sanitized_name.strip()
        try:
            safe_name = urllib.quote_plus(sanitized_name)
            google_results = JSON.ObjectFromURL(GOOGLE_JSON_AMVS % safe_name)[
                'responseData']['results']
        except:
            return None
        for result in google_results:
            url = result['url']
            vid = None
            # members_videoinfo.php or download.php
            if url.startswith('http://www.animemusicvideos.org/members/'):
                try:
                    params = url.split('%3F', 2)[1].split('%26')
                    for param in params:
                        key, value = param.split('%3D')
                        if key == 'v':
                            vid = int(value)
                except:
                    continue
            elif url.startswith('http://www.animemusicvideos.org'
                                '/video/'):
                try:
                    vid = int(url.split('/')[-1])
                except:
                    continue
            if vid is None:
                continue
            try:
                title = result['titleNoFormatting'].split('Information: ')[1]
            except:
                title = result['titleNoFormatting']
            match = re.match(r'.+Video Information: (.*?)(?: - AnimeMusicVideos.org)?$', result['titleNoFormatting'])
            try:
                title = match.group(1)
            except:
                pass
            results.Append(MetadataSearchResult(
                id=str(vid),
                name=title,
                year=None,
                score=100-Util.LevenshteinDistance(title.lower(),
                                                   sanitized_name),
                lang=lang
            ))

    def update(self, metadata, media, lang):
        if not metadata.id:
            return
        """try:
            info_html = HTML.ElementFromURL(AMV_INFO_URL % metadata.id)
            info_html = info_html.cssselect('#info2')[0]
        except:
            Log('Could not pull info for %s' % metadata.id)
        Log(info_html.text_content())"""
        try:
            info_html = HTML.ElementFromURL(AMV_FULL_URL % metadata.id)
            info_html = info_html.cssselect('#main')[0]
        except:
            Log('Could not pull info for %s' % metadata.id)
            return

        # .videoTitle
        metadata.title = info_html.cssselect(
            '.videoTitle')[0].text_content()

        # videoPremiere
        metadata.originally_available_at = Datetime.ParseDate(
            info_html.cssselect('.videoPremiere')[0].text_content()).date()
        metadata.year = metadata.originally_available_at.year

        # videoStudio
        try:
            metadata.studio = info_html.cssselect(
                '.videoStudio')[0].text_content()
        except:
            pass

        # Summary
        try:
            metadata.summary = info_html.cssselect(
                '.comments')[0].text_content()
        except:
            pass

        # .opinionValues
        if 0:  # TODO: opinionValues not available to non members?
            metadata.content_rating = info_html.cssselect(
                '.opinionValues li')[2].text_content()

        try:
            # Member
            metadata.directors.clear()
            metadata.directors.add(info_html.cssselect(
                '#videoInformation ul li a')[0].text_content())
        except:
            pass

        # videoCategory
        metadata.genres.clear()
        for cat in info_html.cssselect('.videoCategory li'):
            metadata.genres.add(cat.text_content().strip())

        # Posters (images from first comment)
        valid_urls = []
        try:
            post = info_html.cssselect('.comments')[0]
        except:
            pass
        else:
            for i, img in enumerate(post.cssselect('img')):
                url = img.get('src')
                valid_urls.append(url)
                if url not in metadata.posters:
                    try:
                        metadata.posters[url] = Proxy.Preview(
                            HTTP.Request(url).content, sort_order=i)
                    except:
                        pass
            metadata.posters.validate_keys(valid_urls)
