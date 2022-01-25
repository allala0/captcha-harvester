from harvester_manager import HarvesterManger
from harvester import Harvester

url = 'https://www.google.com/recaptcha/api2/demo'
sitekey = Harvester.get_sitekey(url)

harvester_manager = HarvesterManger(response_callback=lambda x: print(x['response']))
harvester_manager.add_harvester(Harvester(url, sitekey))
harvester_manager.start_harvesters()
harvester_manager.main_loop()
