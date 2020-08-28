# InstagramScraper
Change the line 123 of the middleware of the rotating proxy dependency
if 'proxy' in request.meta and not request.meta.get('_rotating_proxy'): with if 'proxy' in request.meta:
