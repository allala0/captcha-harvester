# Importing local packages
from harvester_manager import HarvesterManger
from harvester import Harvester


url = 'https://www.google.com/recaptcha/api2/demo'
sitekey = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'

harvester_manager = HarvesterManger(response_callback=print)
harvester_manager.add_harvester(Harvester(url, sitekey))
harvester_manager.start_harvesters()
harvester_manager.main_loop()