import ulozto, btdigg

plugs=(ulozto,btdigg)


def resolve(src, url):
    for p in plugs:
        if src==p.__name__:
            return p.resolve(url)
    raise Exception('Unknown source')