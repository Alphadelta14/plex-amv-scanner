
import re
import urllib

# We try and exclusively query google to avoid thrashing animemusicvideos.org
GOOGLE_JSON_AMVS = 'http://ajax.googleapis.com/ajax/services/search/web'\
    '?v=1.0&rsz=large&q="site:animemusicvideos.org"+video+information+%s'


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
            if url.startswith('http://www.animemusicvideos.org'
                              '/members/members_videoinfo.php'):
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
            Log([title, match.groups() if match else None])
            results.Append(MetadataSearchResult(
                id=str(vid),
                name=title,
                year=None,
                score=100-Util.LevenshteinDistance(title.lower(),
                                                   sanitized_name),
                lang=lang
            ))

    def update(self, metadata, media, lang):
        pass
