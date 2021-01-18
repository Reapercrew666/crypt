import codecs

from slyguy import plugin, inputstream
from slyguy.session import Session
from slyguy.mem_cache import cached
from slyguy.language import _

from .constants import M3U8_URL

session = Session()

@plugin.route('')
def home(**kwargs):
    folder = plugin.Folder(cacheToDisc=False)

    channels = get_channels()
    for slug in sorted(channels, key=lambda k: (float(channels[k].get('channel', 'inf')), channels[k]['name'])):
        channel = channels[slug]

        folder.add_item(
            label    = channel['name'],
            path     = plugin.url_for(play, slug=slug, _is_live=True),
            info     = {'plot': channel.get('description')},
            video    = channel.get('video', {}),
            audio    = channel.get('audio', {}),
            art      = {'thumb': channel.get('logo')},
            playable = True,
        )

    folder.add_item(label=_.SETTINGS,  path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False)

    return folder

@plugin.route()
def play(slug, **kwargs):
    channel = get_channels()[slug]
    url = session.get(channel['mjh_master'], allow_redirects=False).headers.get('location', '')

    item = plugin.Item(
        path      = url,
        headers   = channel['headers'],
        info      = {'plot': channel.get('description')},
        video     = channel.get('video', {}),
        audio     = channel.get('audio', {}),
        art       = {'thumb': channel.get('logo')},
        use_proxy = True,
    )

    if channel.get('hls', False):
        item.inputstream = inputstream.HLS(live=True)

    return item

@cached(60*5)
def get_channels():
    return session.gz_json(M3U8_URL)

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    channels = get_channels()

    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U\n')

        for slug in sorted(channels, key=lambda k: (float(channels[k].get('channel', 'inf')), channels[k]['name'])):
            channel = channels[slug]

            f.write(u'#EXTINF:-1 tvg-id="{id}" tvg-chno="{chno}" tvg-logo="{logo}",{name}\n{path}\n'.format(
                id=slug, logo=channel.get('logo', ''), name=channel['name'], chno=channel.get('channel', ''), 
                    path=plugin.url_for(play, slug=slug, _is_live=True)))