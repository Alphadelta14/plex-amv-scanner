
GOOGLE_JSON_AMVS = 'http://ajax.googleapis.com/ajax/services/search/web'\
    '?v=1.0&rsz=large&q="site:animemusicvideos.org"+%s'


def Start():
    pass


class AMVAgent(Agent.Movies):
    name = 'Anime Music Videos'
    languages = [Locale.Language.English]

    def search(self, results, media, lang, manual):
        pass

    def update(self, metadata, media, lang):
        pass
