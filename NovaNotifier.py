from sys import platform
from asyncio import gather, sleep, create_task, BoundedSemaphore, TimeoutError
from datetime import datetime
from statistics import median
from os import path
from aiohttp import ClientSession
from PyQt5.QtGui import QPixmap
from json import load, dump, JSONDecodeError
import pytz


if platform == "win32":
    from win10toast_persist import ToastNotifier

    
class Optional():
    async def set_date(self):
        today = datetime.now(pytz.timezone('US/Pacific'))
        with open('Files/Medians_refresh.txt', 'w+') as f:
            f.write(f'{today.day}-{today.month}-{today.year}')


class NovaNotifier():

    def __init__(self):
        self.notify = []
        self.network_count = {}
        self.settings = {}
        self.status_lbl = None
        self.db = None
        self.channel = None
        self.sema = None
        self.usernames = []
        self.usernames_error = []
        self.cookies = []
        self.items = {}
        self.result = []

    async def start(self):
        self.sema = BoundedSemaphore(5)

        self.read_settings()
        await self.login()

        if not self.items:
            self.read_id()
            self.read_icons()

        self.filter_medians(self.items)
        await self.network_items(self.items, self.cookies[0])
        self.filter_medians(self.items)

        self.set_names(self.items)
        self.medians_history(self.items)
        self.format(self.items)
        self.make_table(self.items)
        self.save_data(self.items)

    async def refresh(self):
        await self.network_items(self.items, self.cookies[0])
        self.medians_history(self.items)
        self.set_names(self.items)
        self.filter_medians(self.items)
        self.format(self.items)
        self.make_table(self.items)
        self.save_data(self.items)

    async def login(self):
        """ return usernames, cookies """

        if self.settings['browser'] == 'none':
            cookie_val = (await self.db.nova.notifier.find_one({'name': 'cookie'}))['fluxSessionData']
            cookie = {"fluxSessionData": cookie_val}
            # html = await self.network_session('https://novaragnarok.com', cookie)
            # username = html.split("</strong>", 1)[0].rsplit(">", 1)[1]
            # if '\\n' not in username:
            username = 'NovaNotifier'
            self.cookies.append(cookie)
            self.usernames.append(username)
            # else:
            #    raise IndexError('NOVA COOKIE INVALID!')
            return

        from browsercookie3 import chrome, firefox
        cjs = []

        if self.settings['browser'] == 'firefox':
            try:
                cjs.append(firefox(domain_name='novaragnarok.com'))
            except BaseException:
                raise NameError('Firefox Error!')

        else:
            profile = 'Default'
            for i in range(10):
                try:
                    cjs.append(chrome(domain_name='novaragnarok.com', profile=profile))
                except:
                    pass
                profile = f'Profile {i}'

        if not cjs:
            raise NameError('Cookies Not Found!')

        cookie = []
        for item in cjs:
            try:
                cookie.append({"fluxSessionData": item._cookies['www.novaragnarok.com']['/']['fluxSessionData'].value})
            except KeyError:
                pass

        site = 'https://www.novaragnarok.com/?module=account&action=view'
        login = (await gather(*[self.network_session(site, each) for each in cookie]))

        for i, item in enumerate(login):
            try:
                username = item.split("</strong>", 1)[0].rsplit(">", 1)[1]
                if '\\n' not in username and username not in self.usernames:
                    self.usernames.append(username)
                    self.cookies.append(cookie[i])
            except:
                pass

        if not self.usernames:
            raise NameError('Cookies Invalid!')

    def read_id(self):
        with open('Files/ID.json', 'r') as f:
            try:
                self.items = load(f)
            except JSONDecodeError:
                pass

    def read_settings(self):
        """ dict: SM, LM, median_filter, timer_interval, sell_filter, token and browser"""

        # settings = {'SM': 15, 'LM': 60, 'median_filter': 0, 'timer_refresh': 180,
        #           'sell_filter': 0, 'token': 0, 'browser': 'none'}

        with open('Files/Settings.json', 'r') as f:
            self.settings = load(f)

    def write_settings(self):
        with open('Files/Settings.json', 'w') as f:
            dump(self.settings, f, indent=4)

    def read_icons(self):
        for item in self.items.values():
            if 'icon' not in item.keys():
                if path.exists('Icons/' + item['id'] + '.png'):
                    item['icon'] = QPixmap('Icons/' + item['id'] + '.png')

    def filter_medians(self, items):
        # for key, value in items.items():
        #    if self.items['long_med'] < self.settings['median_filter']:
        #        del self.items[key]
        pass

    async def network_session(self, url, cookie):
        async with ClientSession(cookies=cookie) as session:
            html = await self.network_request(url, session)
        return html

    async def network_request(self, url, session):
        fail = 0
        while fail < 3:
            async with self.sema:
                try:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            return str(await response.content.read())
                        else:
                            fail += 1
                            await sleep(3)
                except TimeoutError:
                    await sleep(3)
                    fail += 1
        raise NameError('Retrieving Page Failed 3 Times')

    async def network_market_request(self, item, session):
        url = "https://www.novaragnarok.com/?module=vending&action=item&id=" + item['id']
        fail = 0
        while fail < 3:
            try:
                async with self.sema:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            item['market_data'] = str(await response.content.read())
                            self.status_lbl[0] = (f"Retrieving ({str(self.network_count['each'])}" +
                                                  f"/{str(self.network_count['total'])})")
                            self.network_count['each'] += 1
                            return
                        else:
                            print(response.status)
                            fail += 1
                            await sleep(3)
            except TimeoutError:
                await sleep(3)
                fail += 1
        raise NameError('Retrieving Market Failed 3 Times')

    async def network_history_request(self, item, session):
        if item['long_med'] is None:
            url = "https://www.novaragnarok.com/?module=vending&action=itemhistory&id=" + item['id']
            fail = 0
            while fail < 3:
                async with self.sema:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                item['history_data'] = str(await response.content.read())
                                self.status_lbl[0] = (f"Retrieving ({str(self.network_count['each'])}" +
                                                      f"/{str(self.network_count['total'])})")
                                self.network_count['each'] += 1
                                return
                            else:
                                fail += 1
                                await sleep(3)
                    except TimeoutError:
                        await sleep(3)
                        fail += 1
            raise NameError('Retrieving History Failed 3 Times')

    async def network_icon_request(self, item, session):
        if 'icon' not in item.keys():
            icon_url = 'https://www.novaragnarok.com/data/items/icons2/' + item['id'] + '.png'
            fail = 0
            while fail < 3:
                async with self.sema:
                    try:
                        async with session.get(icon_url, timeout=4) as response:
                            if response.status == 200:
                                icon_file = await response.read()
                                with open('Icons/' + item['id'] + '.png', 'wb+') as f:
                                    f.write(icon_file)
                                item['icon'] = QPixmap('Icons/' + item['id'] + '.png')
                                return
                            else:
                                fail += 1
                                await sleep(3)
                    except TimeoutError:
                        await sleep(3)
                        fail += 1
            raise NameError('Retrieving Icon Failed 3 Times')
        
    async def network_items(self, items, cookie):
        self.network_count = {'each': 1, 'total': len(items)}

        for item in items.values():
            if item['long_med'] is None:
                self.network_count['total'] += 1

        self.status_lbl[0] = (f"Retrieving ({str(self.network_count['each'])}" +
                              f"/{str(self.network_count['total'])})")

        async with ClientSession(cookies=cookie) as session:
            await gather(*[self.network_market_request(item, session) for item in items.values()])

        async with ClientSession(cookies=cookie) as session:
            await gather(*[self.network_history_request(item, session) for item in items.values()])

        async with ClientSession() as session:
            await gather(*[self.network_icon_request(item, session) for item in items.values()])

    def set_names(self, items):
        for item in items.values():
            if item['name'] == 'Unknown':
                item['name'] = item['market_data'].split('"item-name">')[1].split('<')[0]

    def medians_history(self, items):
        for item in items.values():
            if item['long_med'] is None:
                item['short_med'], item['long_med'] = self.medians(item['history_data'], item['refine'], item['property'])

                # if 'icon' not in item.keys():
                #    if path.exists('Icons/' + item['id'] + '.png'):
                #        item['icon'] = QPixmap('Icons/' + item['id'] + '.png')

    def medians(self, history, refine, prop):
        med, long_med = [], []
        today = datetime.now(pytz.timezone('US/Pacific')).replace(minute=0, second=0, microsecond=0)
        prop_column = '<th>Additional Properties</th>' in history
        find_price = history.split('</span>z')
        size = len(find_price) - 2

        i = 0
        # Refine column present
        if '>Refine</th>' in history:
            while i < size:
                item_refine = int(find_price[i + 1].split('data-order="', 1)[1].split('"', 1)[0])
                if item_refine == refine:
                    if self.property_check(prop_column, prop, find_price[i + 1]):
                        date = find_price[i].rsplit(' - ', 1)[0].rsplit(">", 1)[1].split('/')
                        if self.date(date, self.settings['LM'], today):
                            long_med.append(int(find_price[i].rsplit('>', 1)[-1].replace(',', '')))
                            if self.date(date, self.settings['SM'], today):
                                med.append(int(find_price[i].rsplit('>', 1)[-1].replace(',', '')))
                        else:
                            break
                i += 1

        # Refine column missing
        else:
            while i < size:
                if self.property_check(prop_column, prop, find_price[i + 1]):
                    date = find_price[i].rsplit(' - ', 1)[0].rsplit(">", 1)[1].split('/')
                    if self.date(date, self.settings['LM'], today):
                        long_med.append(int(find_price[i].rsplit('>', 1)[-1].replace(',', '')))
                        if self.date(date, self.settings['SM'], today):
                            med.append(int(find_price[i].rsplit('>', 1)[-1].replace(',', '')))
                    else:
                        break
                i += 1

        if med and long_med:
            return round(median(med)), round(median(long_med))
        elif med and not long_med:
            return round(median(med)), 0
        elif not med and long_med:
            return 0, round(median(long_med))
        elif not med and not long_med:
            return 0, 0

    def medians_reset(self):
        with open('Files/ID.json', 'r') as f:
            try:
                items = load(f)
                for item in items.values():
                    item['short_med'] = None
                    item['long_med'] = None
            except JSONDecodeError:
                return

        with open('Files/ID.json', 'w+') as f:
            dump(items, f, indent=4)

        for item in self.items.values():
            item['short_med'], item['long_med'] = None, None

    def discord_reset(self):
        self.settings['token'] = None
        self.write_settings()

    async def sold_notification(self, cookie, username, show_usernames, pause):
        start = datetime.now(pytz.timezone('US/Pacific')).replace(second=0, microsecond=0)
        url = 'https://www.novaragnarok.com/?module=account&action=sellinghistory'

        k = 0
        item = {}
        while True:
            await pause.wait()

            try:
                html = await self.network_session(url, cookie)
            except:
                self.usernames_error.append(username)
                self.usernames.remove(username)
                await show_usernames()
                break

            i = j = back = found = 0
            items = []
            while True:
                try:
                    search = html.rsplit('Selling History', 1)[1].split('data-order', i + 1)[i + 1]
                    time = search.split('</td>', 1)[0].rsplit('>', 1)[1]
                    item['name'] = search.split('</a>', 1)[0].rsplit('\\n', 1)[1].replace('\\t', '').replace('\\', '').strip()
                    item['prop'] = search.split('data-order', 1)[1].split('>', 1)[1].split('<', 1)[0]
                    item['ea'] = search.split('data-order', 1)[1].split('<td>', 1)[1].split('</td>', 1)[0]
                    item['price'] = search.split('</span>z', 2)[1].rsplit('>', 1)[1]
                    # ea_price = start.split('</span>z', 1)[0].rsplit('>', 1)[1]
                    if self.date(time, start, args=1):  # Check if item time is newer than program start time
                        if not back:  # First count all new items since program start running
                            j += 1
                            i += 4  # Next item 4 'data-orders' ahead
                            continue
                    if found:
                        k += 1
                        if int(item['price'].replace(',', '')) >= self.settings['sell_filter'] * 0.97:
                            items.append(item)

                        if j == k:
                            found = 0
                        else:
                            i += 4  # More items to notify, go to next one
                            continue

                    if j > k:
                        found, back, i = 1, 1, 0  # Return to list start to send notifications
                        continue

                    if items:
                        create_task(self.notification(items))

                except IndexError:  # Player could have sold nothing in game yet
                    pass

                await sleep(30)
                break

    async def price_notification(self):
        msg = []
        for key, item in self.items.items():
            if item['price'] and item['alert'] > item['price']:
                if key not in self.notify:
                    msg.append(item)
                    self.notify.append(key)
        if msg:
            create_task(self.notification(msg))

    async def notification(self, items):
        if self.channel:
            for item in items:
                if 'id' in item.keys():  # Market Alert
                    location = item['location'].replace('\n', '')
                    url = 'https://www.novaragnarok.com/?module=vending&action=item&id=' + item['id']
                    msg = (f"Item: {item['format_refine']} {item['name']}\nProperty: {item['format_property']}\n" +
                           f"Location: {location}\nAlert: {item['format_alert']}\nPrice: {item['format_price']}\n{url}")
                    await self.db.nova.users.update_one({'channel': self.channel}, {'$push': {'price_alert': msg}, '$set': {'price_flag': True}})
                else:  # Sold Alert
                    msg = f"Item: {item['ea']}x {item['name']}\nProp: {item['prop']}\nPrice: {item['price']}"
                    await self.db.nova.users.update_one({'channel': self.channel}, {'$push': {'sold_alert': msg}, '$set': {'sold_flag': True}})

        if platform == "win32":
            toast = []
            i = 0
            for i, item in enumerate(items):
                toast.append(ToastNotifier())
                if 'id' in item.keys():  # Market Alert
                    location = item['location'].replace('\n', '')
                    msg = (f"{item['format_refine']} {item['name']}\nProp: {item['format_property']}\n\n" +
                           f"{item['format_price']} | {location}")  # Price notification
                else:  # Sold Alert
                    msg = f"{item['ea']}x {item['name']}\nProp: {item['prop']}\n\nSold: {item['price']}z"  # Sold notification

                toast[i].show_toast("NovaMarket", msg, threaded=True, icon_path='Icons/icon.ico', duration=None)
                await sleep(2)

    async def account_zeny(self):
        if self.channel:
            url = 'https://www.novaragnarok.com/?module=account&action=view'
            accounts = {}
            for cookie, username in zip(self.cookies, self.usernames):
                html = await self.network_session(url, cookie)
                #  character_name = html.split('"link-to-character">')[1].split("</a>")[0]
                #  character_zeny = html.split('"link-to-character">')[1].split('<td>')[4].split('</td>')[0]
                total_zeny = html.split("<strong>")[1].split("</strong>")[0] + 'z'
                accounts[username] = total_zeny

            await self.db.nova.users.update_one({'channel': self.channel}, {'$set': {'accounts': accounts}})

    def date(self, date, interval, today=None, args=None):
        if not args:
            date = pytz.timezone('US/Pacific').localize(datetime(2000 + int(date[2]),
                                                                 int(date[0]),
                                                                 int(date[1])))
            time = today - date

            if time.days <= interval:
                return 1
            else:
                return 0
        else:
            date1 = date.split('-')[0].replace(' ', '').split('/')
            date2 = date.split('-')[1].replace(' ', '').split(':')
            date1[2] = '20' + date1[2]
            date = pytz.timezone('US/Pacific').localize(datetime(int(date1[2]),
                                                                 int(date1[0]),
                                                                 int(date1[1]),
                                                                 hour=int(date2[0]),
                                                                 minute=int(date2[1])))
            if date >= interval:
                return 1  # sold
            else:
                return 0  # old

    def format(self, items):
        for item in items.values():
            pos, format_refine, ea, cheap = self.price_search(item)

            item['format_refine'] = format_refine
            item['format_property'] = ', '.join(item['property'])
            if pos is not None:
                item['format_price'] = format(item['price'], ',d') + 'z'
                item['ea'] = ea
                item['cheap'] = cheap
                item['format_short_med'] = format(item['short_med'], ',d') + 'z'
                item['format_long_med'] = format(item['long_med'], ',d') + 'z'
                item['short_med_perc'], item['long_med_perc'] = self.percentage(item)
                item['format_alert'] = format(item['alert'], ',d') + 'z'
                item['location'] = self.place(item['market_data'], pos)
            else:
                item['format_price'] = '-'
                item['ea'] = '-'
                item['cheap'] = '-'
                item['format_short_med'] = format(item['short_med'], ',d') + 'z'
                item['format_long_med'] = format(item['long_med'], ',d') + 'z'
                item['short_med_perc'], item['long_med_perc'] = '-', '-'
                item['format_alert'] = format(item['alert'], ',d') + 'z' if item['alert'] else '-'
                item['location'] = '-'

    def price_search(self, item):
        find_price_refine = item['market_data'].split('</span>z')
        prop_column = 'Additional Properties' in item['market_data']
        info = {'pos': None, 'cheap_total': 0, 'cheapest_total': 0, 'minor_price': 10000000000}
        minor_refine = item['refine']
        format_refine = f"+{item['refine']}"
        item['price'] = None

        # Check if Market Available
        try:
            refine_exist = item['market_data'].split('</span>z')[1].split('text-align:')[1].split(';')[0]
        except:
            return None, format_refine, '-', '-'

        i = total = 0
        if refine_exist == 'center':  # Refinable
            while i < len(find_price_refine) - 1:
                refine = int(find_price_refine[i + 1].split('data-order="', 1)[1].split('"', 1)[0])
                if refine >= item['refine']:
                    if self.property_check(prop_column, item['property'], find_price_refine[i + 1]):
                        self.lowest_price(find_price_refine[i], find_price_refine[i + 1], item['short_med'], i, info)
                        total += 1
                        minor_refine = refine
                i += 1

            if minor_refine != item['refine']:
                format_refine = f"+{item['refine']} -> +{minor_refine}"
            else:
                format_refine = '+' + str(minor_refine)

        elif refine_exist == 'right' and not item['refine']:  # Not Refinable
            while i < len(find_price_refine) - 1:
                if self.property_check(prop_column, item['property'], find_price_refine[i + 1]):
                    self.lowest_price(find_price_refine[i], find_price_refine[i + 1], item['short_med'], i, info)
                    total += 1
                i += 1

        item['price'] = info['minor_price'] if info['minor_price'] != 10000000000 else 0
        cheap = f'{info["cheapest_total"]}/{info["cheap_total"]}'

        return info['pos'], format_refine, str(total), cheap

    def lowest_price(self, find_price_refine, find_price_refine_next, med, i, info):
        price = int(find_price_refine.rsplit('>', 1)[-1].replace(',', ''))
        try:
            ea = int(find_price_refine_next.split('<td style', 1)[0].split(' ea.')[0].rsplit(' ')[-1])
        except:
            ea = 1
        if price <= med:  # Cheap
            info['cheap_total'] += ea
            if price == info['minor_price']:
                info['cheapest_total'] += ea
            elif price < info['minor_price']:
                info['pos'] = i
                info['minor_price'] = price
                info['cheapest_total'] = ea
        else:  # Expensive
            if price < info['minor_price']:
                info['pos'] = i
                info['minor_price'] = price

    def property_check(self, prop_column, properties, find_price_refine):
        # No Property Column
        if not prop_column:
            if 'None' in properties or 'Any' in properties:
                return 1
            else:
                return 0

        # Property Column
        else:
            pos = {}  # Dict for duplicate properties
            for prop in properties:  # Check if every property is present
                if prop.lower() == 'any':
                    pass

                elif prop not in pos.keys():  # Not a duplicate property
                    i = find_price_refine.split('span class', 1)[0].find(prop)
                    if i != -1:
                        pos[prop] = i  # Save last property position
                    else:
                        return 0

                else:  # Duplicate property, search after last one
                    i = find_price_refine.split('span class', 1)[0][pos[prop] + 1: -1].find(prop)
                    if i != -1:
                        pos[prop] = i
                    else:
                        return 0
        return 1

    def percentage(self, item):
        if item['long_med']:
            if item['long_med'] > item['price']:
                long_med_perc = '-' + str(round(abs(100 - (item['price'] / item['long_med']) * 100))) + '%'
            elif item['long_med'] < item['price']:
                long_med_perc = '+' + str(round(abs(100 - (item['price'] / item['long_med']) * 100))) + '%'
            else:
                long_med_perc = '0%'
        else:
            return '0%', '0%'

        if long_med_perc == '+0%' or long_med_perc == '-0%':
            long_med_perc = '0%'

        if item['short_med']:
            if item['short_med'] > item['price']:
                med_perc = '-' + str(round(abs(100 - (item['price'] / item['short_med']) * 100))) + '%'
            elif item['short_med'] < item['price']:
                med_perc = '+' + str(round(abs(100 - (item['price'] / item['short_med']) * 100))) + '%'
            else:
                med_perc = '0%'
        else:
            med_perc = '0%'

        if med_perc == '+0%' or med_perc == '-0%':
            med_perc = '0%'

        return med_perc, long_med_perc

    def place(self, market_data, pos):
        find_place = market_data.split("data-map=")
        places = find_place[pos + 1].replace(' ', '').split("</span>")[0].split(">")[1].split(',')
        return f"{places[0]}\n[{places[1]},{places[2]}]".replace('\\n', '')

    def make_table(self, items):
        self.result = []
        for item in items.values():
            self.result.append(
                [item['id'], item['name'], item['format_refine'], item['format_property'], item['format_price'],
                 item['ea'], item['cheap'], item['format_short_med'], item['format_long_med'],
                 item['short_med_perc'], item['long_med_perc'], item['format_alert'], item['location'], ""])

    def save_data(self, items):
        save = {}
        for key, value in items.items():
            save[key] = {'id': value['id'],
                         'name': value['name'],
                         'refine': value['refine'],
                         'alert': value['alert'],
                         'property': value['property'],
                         'short_med': value['short_med'],
                         'long_med': value['long_med']}

        with open('Files/ID.json', 'w+') as f:
            dump(save, f, indent=4)
