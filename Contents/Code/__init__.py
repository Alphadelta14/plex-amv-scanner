
import re

# We try and exclusively query google to avoid thrashing animemusicvideos.org
GOOGLE_JSON_AMVS = 'http://ajax.googleapis.com/ajax/services/search/web'\
    '?v=1.0&rsz=large&q="site:animemusicvideos.org"+video+information+%s'


def Start():
    pass


class AMVAgent(Agent.Movies):
    name = 'Anime Music Videos'
    languages = [Locale.Language.English]

    def search(self, results, media, lang, manual):
        try:
            google_results = JSON.ObjectFromURL(GOOGLE_JSON_AMVS % media.name)[
                'responseData']['results']
        except:
            return None
        for result in google_results:
            url = result['url']
            if not url.startswith('http://www.animemusicvideos.org'
                                  '/members/members_videoinfo.php'):
                continue
            vid = None
            try:
                params = url.split('%3F', 2)[1].split('%26')
                for param in params:
                    key, value = param.split('%3D')
                    if key == 'v':
                        vid = int(value)
            except:
                continue
            if vid is None:
                continue
            try:
                title = result['titleNoFormatting'].split('Information: ')[1]
            except:
                title = result['titleNoFormatting']
            results.Append(MetadataSearchResult(
                id=str(vid),
                name=title,
                year=2000,
                score=Util.LevenshteinDistance(title.lower(),
                                               media.name.lower()),
                lang=lang
            ))

    def update(self, metadata, media, lang):
        pass
