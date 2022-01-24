from harvester import Harvester
from harvester_manager import HarvesterManger
from bot import Bot


url = 'https://www.google.com/recaptcha/api2/demo'
sitekey = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'

bot = Bot(url, sitekey)
bot.start(url=url)
bot.run_loops()