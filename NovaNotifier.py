from sys import platform
from asyncio import gather, sleep, BoundedSemaphore
from qasync import asyncSlot
from datetime import datetime, timedelta
from statistics import median
from os import path
from aiohttp import ClientSession
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

    def __init__(self, main):
        self.main = main
        self.progress = ''
        self.notify = {}
        self.network_count = 1
        self.settings = {}
        self.sema = None
        self.items = {}
        self.result = []
        self.market_data = {}
        self.history_data = {}
        self.icons_response = {}
        self.names = {}
        self.accounts = {}
        self.usernames = []
        self.cookies = []
        self.icons = {}
        self.sell_htmls = []
        self.account_htmls = []
        self.get_history = True
        self.icon_path = 'Files/Icons/App/main2.ico'

    async def start(self):
        self.sema = BoundedSemaphore(3)

        self.read_settings()
        await self.login()

        if not self.items:
            self.read_item()

        self.get_history = True
        await self.network_items(self.items, self.cookies[0])

        self.set_icons()
        self.set_names()
        self.medians_history(self.items)
        self.formatting(self.items)
        self.make_table(self.items)
        self.save_data(self.items)
        await self.notification()
        await self.account_data()

    async def refresh(self):
        self.get_history = False
        await self.network_items(self.items, self.cookies[0])
        self.formatting(self.items)
        self.make_table(self.items)
        await self.notification()

    async def login(self):
        """ set usernames and cookies """

        self.main.lbl_refresh.setText('Login in Progress')
        if self.settings['browser'] == 'none':
            cookie_val = (await self.main.db.nova.notifier.find_one({'name': 'cookie'}))['fluxSessionData']
            cookie = {"fluxSessionData": cookie_val}
            html = await self.network_session('https://novaragnarok.com', cookie)
            if html.find("Welcome!") != -1:
                self.usernames.append("NovaNotifier")
                self.cookies.append(cookie)
                self.accounts["NovaNotifier"] = cookie
            else:
                raise IndexError('NovaNotifier Cookie Expired!')
            return

        from browsercookie3 import chromium, chrome, firefox, opera, edge
        cjs = []

        if self.settings['browser'] == 'firefox':
            try:
                cjs.append(firefox(domain_name='novaragnarok.com'))
            except BaseException:
                raise NameError('Firefox Error!')
        elif self.settings['browser'] == 'opera':
            try:
                cjs.append(opera(domain_name='novaragnarok.com'))
            except BaseException:
                raise NameError('Opera Error!')
        elif self.settings['browser'] == 'edge':
            try:
                cjs.append(edge(domain_name='novaragnarok.com'))
            except BaseException:
                raise NameError('Opera Error!')
        elif self.settings['browser'] == 'chromium':
            try:
                cjs.append(chromium(domain_name='novaragnarok.com'))
            except BaseException:
                raise NameError('Chromium Error!')
        else:
            profile = 'Default'
            for i in range(10):
                try:
                    cjs.append(chrome(domain_name='novaragnarok.com', profile=profile))
                except Exception:
                    pass
                profile = f'Profile {i}'

        if not cjs:
            raise NameError('Cookies Not Found!')

        cookies = []
        for item in cjs:
            try:
                cookies.append({"fluxSessionData": item._cookies['www.novaragnarok.com']['/']['fluxSessionData'].value})
            except KeyError:
                pass

        site = 'https://www.novaragnarok.com/?module=account&action=view'
        login = (await gather(*[self.network_session(site, each) for each in cookies]))

        usernames = []
        for i, item in enumerate(login):
            username = item.split("</strong>", 1)[0].rsplit(">", 1)[1]
            if username != '\n' and username not in usernames:
                self.usernames.append(username)
                self.cookies.append(cookies[i])
                self.accounts[username] = {'cookie': cookies[i]}
                if username == 'Nova_Notifier':
                    await self.main.db.nova.notifier.update_one({'name': 'cookie'}, {'$set': {'fluxSessionData': cookies[i]['fluxSessionData']}})

        if not self.accounts:
            raise NameError('Cookies Invalid!')

    def read_item(self):
        try:
            with open('Files/ID.json', 'r') as f:
                self.items = load(f)

            with open('Files/Names.json', 'r') as f:
                self.names = load(f)
        except JSONDecodeError:
            pass

        for item in self.items.values():
            if path.exists(f"Files/Icons/Item/{item['id']}.png"):
                self.icons[item['id']] = True

    def read_settings(self):
        """ dict: SM, LM, timer_refresh, sell_filter, token and browser"""

        with open('Files/Settings.json', 'r') as f:
            self.settings = load(f)

    def write_settings(self):
        with open('Files/Settings.json', 'w') as f:
            dump(self.settings, f, indent=4)

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
                            return await response.text()
                        else:
                            fail += 1
                            await sleep(3)
                except Exception:
                    await sleep(3)
                    fail += 1
        raise NameError('Retrieving Page Failed 3 Times')

    async def network_market_request(self, item, session):
        if item['id'] not in self.market_data:
            url = f"https://www.novaragnarok.com/data/cache/ajax/item_{item['id']}.json"
            self.market_data[item['id']] = True
            fail = 0
            while fail < 3:
                try:
                    async with self.sema:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                self.market_data[item['id']] = (await response.json())['data']
                                self.retrieving()
                                return
                            else:
                                fail += 1
                                await sleep(3)
                except Exception:
                    await sleep(3)
                    fail += 1
            raise NameError('Retrieving Market Failed 3 Times')

    async def network_history_request(self, item, session):
        if self.get_history and item['id'] not in self.history_data:
            self.history_data[item['id']] = True
            url = f"https://www.novaragnarok.com/data/cache/ajax/history_{item['id']}.json"
            fail = 0
            while fail < 3:
                async with self.sema:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                self.history_data[item['id']] = (await response.json())['data']
                                return
                            else:
                                fail += 1
                                await sleep(3)
                    except Exception:
                        await sleep(3)
                        fail += 1
            raise NameError('Retrieving History Failed 3 Times')

    async def network_icon_request(self, item, session):
        if item['id'] not in self.icons:
            icon_url = 'https://www.novaragnarok.com/data/items/icons2/' + item['id'] + '.png'
            if item['id'] not in self.icons:
                self.icons[item['id']] = True
                fail = 0
                while fail < 3:
                    async with self.sema:
                        try:
                            async with session.get(icon_url, timeout=5) as response:
                                if response.status == 200:
                                    self.icons_response[item['id']] = await response.read()
                                    return
                                else:
                                    fail += 1
                                    await sleep(3)
                        except Exception:
                            await sleep(3)
                            fail += 1
                raise NameError('Retrieving Icon Failed 3 Times')

    async def network_name_request(self, item, session):
        if item['id'] not in self.names:
            url = f"https://www.novaragnarok.com/?module=vending&action=item&id={item['id']}"
            fail = 0
            while fail < 3:
                async with self.sema:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                item['name'] = (await response.text()).split('<title>', 1)[1].split(' -', 1)[0]
                                self.names[item['id']] = item['name']
                                return
                            else:
                                fail += 1
                                await sleep(3)
                    except Exception:
                        await sleep(3)
                        fail += 1
            raise NameError('Retrieving Name Failed 3 Times')
        else:
            item['name'] = self.names[item['id']]

    async def network_items(self, items, cookie):
        self.market_data, self.icons_response = {}, {}
        self.network_count = 1

        # Start All Network Search
        async with ClientSession() as session:
            await gather(*[self.network_market_request(item, session) for item in items.values()])

        async with ClientSession() as session:
            await gather(*[self.network_history_request(item, session) for item in items.values()])

        async with ClientSession() as session:
            await gather(*[self.network_icon_request(item, session) for item in items.values()])

        async with ClientSession(cookies=cookie) as session:
            await gather(*[self.network_name_request(item, session) for item in items.values()])

    def retrieving(self):
        self.main.lbl_refresh.setText(f"Retrieving: {self.network_count}")
        self.network_count += 1

    def set_icons(self):
        for key in self.icons_response:
            with open(f"Files/Icons/Item/{key}.png", 'wb+') as f:
                f.write(self.icons_response[key])

    def set_names(self):
        with open('Files/Names.json', 'w') as f:
            dump(self.names, f, indent=4)

    def medians_history(self, items):
        today = datetime.now(pytz.timezone('US/Pacific')).replace(minute=0, second=0, microsecond=0)
        interval = [self.settings['SM'], self.settings['LM']]
        for item in items.values():
            med, long_med = [], []
            if 'Any' in item['property'] or "any" in item['property']:
                pass

            else:
                history = self.history_data[item['id']]
                for each in history:
                    if 'refine' in each['orders']:
                        item_refine = each['orders']['refine']
                        if item_refine == item['refine']:
                            if self.property_check(each, item['property']):
                                date = each['items']['date'].split(' ', 1)[0].split("/")
                                call = self.date(date, interval, today)
                                if call[0] is True:
                                    long_med.append(each['orders']['price'])
                                    if call[1] is True:
                                        med.append(each['orders']['price'])

                    else:
                        if self.property_check(each, item['property']):
                            date = each['items']['date'].split(' ', 1)[0].split("/")
                            call = self.date(date, interval, today)
                            if call[0] is True:
                                long_med.append(each['orders']['price'])
                                if call[1] is True:
                                    med.append(each['orders']['price'])
                            else:
                                break

            if med and long_med:
                item['short_med'], item['long_med'] = round(median(med)), round(median(long_med))
            elif med and not long_med:
                item['short_med'], item['long_med'] = round(median(med), 0)
            elif not med and long_med:
                item['short_med'], item['long_med'] = 0, round(median(long_med))
            elif not med and not long_med:
                item['short_med'], item['long_med'] = 0, 0

    @asyncSlot()
    async def account_data(self):
        try:
            url = 'https://www.novaragnarok.com/?module=account&action=view'
            if self.settings['browser'] != 'none' and self.cookies:
                self.account_htmls = (await gather(*[self.network_session(url, each) for each in self.cookies]))
                await self.account_zeny()
        except Exception:
            self.main.exception()

    async def account_zeny(self):
        for i, username in enumerate(self.usernames):
            characters = []
            characters_zeny = []
            if 'link-to-character' in self.account_htmls[i]:
                name_string = self.account_htmls[i].split('"link-to-character">')
                del name_string[0]
                for name in name_string:
                    characters.append(name.split("</a>")[0])
                    characters_zeny.append(name.split('<td>')[4].split('</td>')[0] + 'z')
                total_zeny = self.account_htmls[i].split("Total Zeny: <strong>")[1].split("</strong>")[0] + 'z'
                self.accounts[username]['characters'] = characters
                self.accounts[username]['characters_zeny'] = characters_zeny
                self.accounts[username]['total_zeny'] = total_zeny
            else:
                self.accounts[username]['characters'] = ['']
                self.accounts[username]['characters_zeny'] = ['']
                self.accounts[username]['total_zeny'] = '0z'

        # await self.main.db.nova.users.update_one({'channel': self.main.channel}, {'$set': {'accounts': accounts}})

    async def sold_notification(self):
        start = datetime.now(pytz.timezone('US/Pacific')).replace(second=0, microsecond=0)
        url = 'https://www.novaragnarok.com/?module=account&action=sellinghistory'
        item = {}
        while self.settings['browser'] != 'none':
            self.sell_htmls = (await gather(*[self.network_session(url, each) for each in self.cookies]))
            for html in self.sell_htmls:
                items = []
                i = 0
                while True:
                    try:
                        search = html.rsplit('Selling History', 1)[1].split('data-order', i + 1)[i + 1]
                        time = search.split('</td>', 1)[0].rsplit('>', 1)[1]
                        item['name'] = search.split('</a>', 1)[0].rsplit('\n', 1)[1].replace('\\t', '').strip()
                        item['prop'] = search.split('data-order', 1)[1].split('>', 1)[1].split('<', 1)[0]
                        item['ea'] = search.split('data-order', 1)[1].split('<td>', 1)[1].split('</td>', 1)[0]
                        item['price'] = search.split('</span>z', 2)[1].rsplit('>', 1)[1]
                        # ea_price = start.split('</span>z', 1)[0].rsplit('>', 1)[1]
                        if self.date(time, start, args=1):  # Check if item time is newer than program start time
                            if int(item['price'].replace(',', '')) >= self.settings['sell_filter'] * 0.97:
                                items.append(item)
                                i += 4  # Next item 4 'data-orders' ahead
                                continue
                        elif items:
                            await self.notification(sell_item=items)
                            # time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    except IndexError:  # Did not sell anything in game yet
                        pass
                    except Exception:
                        return
                    break
            start = start + timedelta(minutes=1)
            await sleep(60)

    async def notification(self, sell_item=None):
        # Save items first to prevent duplicate notifications
        if sell_item:
            items = sell_item
        else:
            items = []
            for key in self.notify:
                if self.notify[key]:
                    items.append(self.items[key])
                    self.notify[key] = False

        for item in items:
            # Price Alert
            if 'id' in item:
                if self.settings['price_notification']:
                    location = item['location'].replace('\n', '')
                    url = 'https://www.novaragnarok.com/?module=vending&action=item&id=' + item['id']
                    if self.settings['discord_notification'] and self.main.discord_channel:
                        msg = (f"{item['name']}\nRefine: {item['format_refine']}\nProperty: {item['format_property']}\n" +
                               f"Alert: {item['format_alert']}\nPrice: {item['format_price']}\nLocation: {location}\n\n{url}")
                        await self.main.db.nova.users.update_one({'channel': self.main.discord_channel}, {'$push': {'price_alert': msg}, '$set': {'price_flag': True}})
                    if self.settings['system_notification'] and platform == "win32":
                        msg = (f"{item['format_refine']} {item['name']}\nProp: {item['format_property']}\n\n" +
                               f"{item['format_price']} | {location}")
                        toast = ToastNotifier()
                        toast.show_toast("NovaMarket", msg, threaded=True, icon_path=self.icon_path, duration=None)
                        await sleep(1)
            # Sell Alert
            elif self.settings['sell_notification']:
                if self.settings['discord_notification'] and self.main.discord_channel:
                    msg = f"{item['ea']}x {item['name']}\nProp: {item['prop']}\nPrice: {item['price']}"
                    await self.main.db.nova.users.update_one({'channel': self.main.discord_channel}, {'$push': {'sold_alert': msg}, '$set': {'sold_flag': True}})
                if self.settings['system_notification'] and platform == "win32":
                    msg = f"{item['ea']}x {item['name']}\nProp: {item['prop']}\n\nSold: {item['price']}z"
                    toast = ToastNotifier()
                    toast.show_toast("NovaMarket", msg, threaded=True, icon_path=self.icon_path, duration=None)
                    await sleep(1)

    def date(self, date, interval, today=None, args=None):
        if not args:
            result = [False, False]
            date = pytz.timezone('US/Pacific').localize(datetime(2000 + int(date[2]),
                                                                 int(date[0]),
                                                                 int(date[1])))
            time = today - date

            if time.days <= interval[1]:
                result[0] = True
                if time.days <= interval[0]:
                    result[1] = True

            return result
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

    def formatting(self, items):
        for key, item in items.items():
            location, format_refine, format_prop = self.price_search(item, key)

            item['format_refine'] = format_refine
            item['format_property'] = ', '.join(format_prop)
            if location is not None:
                item['format_price'] = format(item['price'], ',d') + 'z'
                item['format_short_med'] = format(item['short_med'], ',d') + 'z'
                item['format_long_med'] = format(item['long_med'], ',d') + 'z'
                item['short_med_perc'], item['long_med_perc'] = self.percentage(item)
                item['format_alert'] = format(item['alert'], ',d') + 'z'
                item['location'] = location.split(',', 1)[0] + '\n ' + location.split(',', 1)[1]
            else:
                item['format_price'] = '-'
                item['ea'] = '-'
                item['format_short_med'] = format(item['short_med'], ',d') + 'z'
                item['format_long_med'] = format(item['long_med'], ',d') + 'z'
                item['short_med_perc'], item['long_med_perc'] = '-', '-'
                item['format_alert'] = format(item['alert'], ',d') + 'z' if item['alert'] else '-'
                item['location'] = '-'

    def price_search(self, item, key):
        """ Return: Cheapest Item Location and Format_Refine """

        info = {'median': item['short_med'], 'cheap_total': 0, 'cheapest_total': 0,
                'cheapest_location': None, 'cheapest_price': 1000000000, 'alert': item['alert']}
        minor_refine = item['refine']
        format_refine = f"+{item['refine']}"
        format_prop = item['property']

        for each in self.market_data[item['id']]:
            if 'refine' in each['orders']:
                refine = each['orders']['refine']
                if refine >= item['refine']:
                    if prop := self.property_check(each, item['property']):
                        self.lowest_price(each, info, key)
                        minor_refine = refine
                        format_prop = prop

            else:  # Not Refinable
                if self.property_check(each, item['property']):
                    self.lowest_price(each, info, key)

        if minor_refine != item['refine']:
            format_refine = f"+{item['refine']} -> +{minor_refine}"
        else:
            format_refine = f"+{minor_refine}"

        item['price'] = info['cheapest_price']
        item['ea'] = f'{info["cheapest_total"]} / {info["cheap_total"]}'

        return info['cheapest_location'], format_refine, format_prop

    def lowest_price(self, item, info, item_key):
        if 'qty' in item['orders']:
            ea = item['orders']['qty']
        else:
            ea = 1

        info['cheap_total'] += ea
        price = item['orders']['price']

        if price == info['cheapest_price']:
            info['cheapest_total'] += ea

        elif price < info['cheapest_price']:
            info['cheapest_price'] = price
            info['cheapest_location'] = item['orders']['location'].strip()
            info['cheapest_total'] = ea

        if info['cheapest_price'] < info['alert'] and item_key not in self.notify:
            self.notify[item_key] = True

    def property_check(self, web_prop, prop):
        """ Input: Properties from Website, Your Item Properties """

        item_prop = list(prop)
        # No Property Column
        if 'property' not in web_prop['orders']:
            if 'None' in item_prop:
                return prop
            else:
                return 0

        elif 'property' in web_prop['orders'] and not web_prop['orders']['property']:
            if 'None' in item_prop:
                return prop
            else:
                return 0

        # Property Column
        else:
            try:
                end = web_prop['items']['property'].split("</a>, ")[-1].split('<')[0].split('. ')
            except Exception:
                pass  # Must be here the problem

            web_result = []
            first_split = web_prop['items']['property'].split("'>")[1:]
            for each in first_split:
                web_result.append(each.split('</a>')[0])

            if not web_result:
                web_result = web_prop['items']['property'].split('>')[1].split('<')[0].split('. ')
                web_result[-1] = web_result[-1].rstrip('.')
            elif end[0]:
                end[-1] = end[-1].rstrip('.')
                web_result.extend(end)

            # Comparison between item from website and requested property
            extra = False
            for item in item_prop:
                if item.upper() == 'ANY':
                    extra = True
                    continue
                else:
                    if item in web_result:
                        web_result.remove(item)
                        continue
                    else:
                        return 0

            if web_result and not extra:
                return 0

            if web_result:
                return item_prop + web_result

            return item_prop

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

    def make_table(self, items):
        # Make table to main
        self.result = []
        for key, item in items.items():
            self.result.append(
                [item['id'], item['name'], item['format_refine'], item['format_property'],
                 item['format_price'], item['ea'], item['format_short_med'], item['format_long_med'],
                 item['short_med_perc'], item['long_med_perc'], item['format_alert'], item['location'], key])

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
