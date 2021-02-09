from datetime import datetime
from discord import Embed, Client, Intents
from secrets import token_hex
from asyncio import create_task, sleep, run

# could be hidden using environment variables
TOKEN = 'Insert Here Your Discord Bot Token'

intents = Intents.default()
intents.members = True

client = Client(intents=intents)
host_channel = None


class NovaBot():
    def __init__(self, database, channel, notif=None):
        global db, client, host_channel
        db, host_channel = database, channel

        try:
            create_task(client.start(TOKEN))
        except RuntimeError:
            client.run(TOKEN)
        if notif:
            notif.setText('Host: Hosting!')


@client.event
async def on_ready():

    await db.nova.notifier.update_one({'name': 'session'},
                                      {"$set":
                                      {'start_time': datetime.utcnow(),
                                       'host_discord': host_channel}})

    create_task(get_db())


async def get_db():
    global client
    while True:
        await db.nova.notifier.update_one({'name': 'session'},
                                          {"$set":
                                          {'last_update': datetime.utcnow()}})

        users = db.nova.users.find({'price_flag': True})
        for user in await users.to_list(length=100):
            discord_channel = client.get_user(user['channel'])
            embed = Embed(title='Good News!', description='', color=16580705)
            for item in user['price_alert']:
                embed.add_field(name='Alert:', value=item)

            await db.nova.users.update_one({'channel': user['channel']},
                                           {"$set": {'price_alert': [], 'price_flag': False}})

            await discord_channel.send(embed=embed)

        users = db.nova.users.find({'sold_flag': True})
        for user in await users.to_list(length=100):
            discord_channel = client.get_user(user['channel'])
            embed = Embed(title='Sold Alert!', description='', color=16580705)
            for item in user['sold_alert']:
                embed.add_field(name='Alert:', value=item)

            await db.nova.users.update_one({'channel': user['channel']},
                                           {"$set": {'sold_alert': [], 'sold_flag': False}})

            await discord_channel.send(embed=embed)

        await sleep(10)


@client.event
async def on_message(message):
    if message.content.lower() == '!start':
        channel = message.author.id
        message_channel = client.get_user(channel)
        discord = f"{message.author.display_name}#{message.author.discriminator}"
        token = token_hex(2)
        while await db.nova.users.find_one({'token': token}):
            token = token_hex(2)
        await message_channel.send(f"Token: {token}")
        await db.nova.users.replace_one({'channel': channel},
                                        {'channel': channel,
                                         'discord': discord,
                                         'token': token,
                                         'date': datetime.utcnow(),
                                         'price_alert': [],
                                         'sold_alert': [],
                                         'price_flag': False,
                                         'sold_flag': False,
                                         'accounts': False}, upsert=True)

if __name__ == '__main__':
    from motor.motor_asyncio import AsyncIOMotorClient
    TKN_MONGOdb = 'Insert Here Your MongoDB Token'
    db = AsyncIOMotorClient(TKN_MONGOdb)
    run(NovaBot(db))
