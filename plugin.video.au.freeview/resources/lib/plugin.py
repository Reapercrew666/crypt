import codecs

from slyguy import plugin, settings, inputstream
from slyguy.mem_cache import cached
from slyguy.session import Session
from slyguy.util import gzip_extract

from .constants import M3U8_URL, REGIONS, EPG_URL
from .language import _

session = Session()

@cached(200)
def get_token():
    params = {
        'region': 'Sydney',
        'network': 'ABC',
        'channel_id': '101002210220',
        'token': 'L$#_rR7}K3IaB',
        'format': 'json',
    }

    return session.get('https://freeview-fv.global.ssl.fastly.net/288/epgApi/getToken', params=params).json()

@plugin.route('')
def home(**kwargs):
    region  = get_region()
    channels = get_channels(region)

    folder = plugin.Folder(_(_.REGIONS[region]), cacheToDisc=False)

    for slug in sorted(channels, key=lambda k: (channels[k].get('network', ''), channels[k].get('name', ''))):
        channel = channels[slug]

        folder.add_item(
            label = channel['name'],
            path  = plugin.url_for(play, slug=slug, _is_live=True),
            info  = {'plot': channel.get('description')},
            video = channel.get('video', {}),
            audio = channel.get('audio', {}),
            art   = {'thumb': channel.get('logo')},
            playable = True,
        )

    folder.add_item(label=_.SETTINGS,  path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False)

    return folder

@plugin.route()
def play(slug, **kwargs):
    region  = get_region()
    channel = get_channels(region)[slug]
    url = session.get(channel['mjh_master'], allow_redirects=False).headers.get('location', '')

    if channel.get('network') == 'ABC' and channel.get('stream_type') == 'Token' and '?' not in url:
        token = get_token()
        url += '?' + token

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
def get_channels(region):
    return session.gz_json(M3U8_URL.format(region=region))

def get_region():
    return REGIONS[settings.getInt('region_index')]

@plugin.route()
@plugin.merge()
def playlist(output, **kwargs):
    region   = get_region()
    channels = get_channels(region)

    with codecs.open(output, 'w', encoding='utf8') as f:
        f.write(u'#EXTM3U\n')

        for slug in sorted(channels, key=lambda k: (channels[k].get('network', ''), channels[k].get('name', ''))):
            channel = channels[slug]

            f.write(u'#EXTINF:-1 tvg-id="{id}" tvg-chno="{chno}" tvg-logo="{logo}",{name}\n{path}\n'.format(
                id=channel.get('epg_id', slug), logo=channel.get('logo', ''), name=channel['name'], chno=channel.get('channel', ''), 
                    path=plugin.url_for(play, slug=slug, _is_live=True)))

@plugin.route()
@plugin.merge()
def epg(output, **kwargs):
    session.chunked_dl(EPG_URL.format(region=get_region()), output)
    gzip_extract(output)