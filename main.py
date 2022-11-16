from read_emails import *
import datetime
import discord
from discord.ext import commands
import keyring

intents = discord.Intents.default()

client = commands.Bot(case_insensitive=True,
                      command_prefix='&',
                      game=discord.Game(name="Loading..."),
                      intents=intents
                      )
guild_ids = [670116973572653058,
             600796603967602724]


def get_news_channel():
    for e in client.guilds:
        if e.id == 600796603967602724:
            for chan in e.channels:
                if chan.id == 773402321739710465:
                    return chan


def getBPGuild():
    for e in client.guilds:
        if e.id == 600796603967602724:
            return e


@client.event
async def on_ready():
    print("News Bot Operating!")
    emails = getEmails()
    news_channel = get_news_channel()
    today_date = datetime.datetime.now().strftime('%b %#d %Y')
    to_publish = []
    t = await news_channel.send("Blue Politics News Brief for " + today_date)
    to_publish.append(t)
##    try:
##        await t.publish()
##    except Exception as e:
##        print(e)

    regions = {'Top of the Agenda': {'color': 0x888888, 'icon': ':newspaper: '},
               'Europe': {'color': 0x1fc41f, 'icon': ':flag_eu: '},
               'United States': {'color': 0x0656cf, 'icon': ':flag_us: '},
               'Middle East and North Africa': {'color': 0xede615, 'icon': ':camel: '},
               'Americas': {'color': 0x0EFF64, 'icon': ':earth_americas: '},
               'Sub-Saharan Africa': {'color': 0xa95eff, 'icon': ':earth_africa: '},
               'South and Central Asia': {'color': 0xe67409, 'icon': ':earth_asia: '},
               'Pacific Rim': {'color': 0x00F8FF, 'icon': ':island: '},
               'Default': {'color': 0x909090, 'icon': ':newspaper: '}}

    stories = parse_body(emails[0]['decoded'])
    for story in stories:
        headline = ':small_blue_diamond: ' + story['header']
        text = story['text']
        region = story['region']
        region_title = region
        if region not in regions.keys():
            region = 'Default'
        msg = discord.Embed(title=regions[region]['icon'] + region_title,
                            description='**'+headline+'**'+text,
                            color=regions[region]['color'])
        msg.set_footer(text='• ' + today_date +
                            ' • Subscribe to News Brief in #roles to get pinged! • discord.gg/bluepolitics •')
        try:
            msg.set_thumbnail(url=getBPGuild().icon.url)
        except Exception as e:
            print("thumbnail set failed: "+str(e))
        p = await news_channel.send(embed=msg)
        to_publish.append(p)
##        try:
##            await p.publish()
##        except Exception as e:
##            print(e)

    await news_channel.send('<@&999326914487529543> Your daily news brief is above!')
    for i in to_publish:
        try:
            await i.publish()
        except:
            pass
    await client.close()


client.run(keyring.get_password('discord', 'bpbot'))
