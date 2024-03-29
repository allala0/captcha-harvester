# Importing local packages
import harvester
# Importing external packages
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
# Importing standard packages
import time
import datetime
from threading import Thread
import random


class Bot(harvester.Browser):
    def __init__(self, harvester_manager: harvester.HarvesterManger, delay: int = 0.1):

        super(Bot, self).__init__()

        self.harvester_manager = harvester_manager
        self.delay = delay
        self.control_element = f'controlElement{random.randint(0, 10 ** 10)}'

        self.looping = False

    def main_loop(self) -> None:
        if not self.looping:
            self.looping = True
            while self.looping:
                if self.is_open:
                    # Try except to be upgraded...
                    try:
                        self.tick()
                    except WebDriverException as e:
                        print(e)
                        self.looping = False
                time.sleep(self.delay)

    def tick(self):

        inject_list = (
            f'document.getElementsByClassName("g-recaptcha")[0].insertAdjacentHTML("beforebegin", \'<div class="{self.control_element}"></div>\');',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].innerHTML = \'<span class="clicked_{self.control_element}"></span><input type="button" class="button_{self.control_element}" value="Click to inject captcha"><span class="description_{self.control_element}"></span><span class="timestamp_{self.control_element}"></span>\';',

            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.border = \'2px solid #333\';',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.borderRadius = \'20px\';',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.height = \'27px\';',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.marginBottom = \'5px\';',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.padding = \'0\';',
            f'document.getElementsByClassName(\'{self.control_element}\')[0].style.overflow = \'hidden\';',

            f'document.getElementsByClassName(\'clicked_{self.control_element}\')[0].style.display = \'none\';',
            f'document.getElementsByClassName(\'timestamp_{self.control_element}\')[0].style.display = \'none\';',

            f'document.getElementsByClassName(\'description_{self.control_element}\')[0].style.marginLeft = \'5px\';',

            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.boxSizing = \'border-box\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].onclick = function(){{document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML = "clicked";}};',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.borderRadius = \'20px\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.margin = \'0\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.padding = \'0\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.cursor = \'pointer\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.padding = \'5px\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.backgroundColor = \'#333\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.color = \'white\';',
            f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.border = \'none\';'
        )

        if not self.execute_script(f'return document.getElementsByClassName("{self.control_element}")'):
            for inject_html in inject_list:
                self.execute_script(inject_html)

        if not self.execute_script('return grecaptcha.getResponse();'):

            self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].style.cursor = "pointer"')

            self.execute_script(f'document.getElementsByClassName("{self.control_element}")[0].style.border = "2px solid #333"')
            self.execute_script(f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.backgroundColor = \'#333\';', )
            self.execute_script(f'document.getElementsByClassName("description_{self.control_element}")[0].innerHTML = "Captchas harvested: {len(self.harvester_manager.response_queue)}"')
            if self.execute_script(f'return document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML;'):
                self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Waiting for captcha"')
            else:
                self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Click to inject captcha"')
        else:
            now = datetime.datetime.now()
            timestamp = self.execute_script(f'return document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML;')
            if timestamp:
                timestamp_string = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                delta = now - timestamp_string
                self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Captha injected"')
                self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].style.cursor = "default"')
                self.execute_script(f'document.getElementsByClassName("description_{self.control_element}")[0].innerHTML = "Captha expires in {120 - delta.seconds} seconds"')
                self.execute_script(f'document.getElementsByClassName("{self.control_element}")[0].style.border = "2px solid green"')
                self.execute_script(f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.backgroundColor = \'green\';', )

        if self.execute_script(f'return document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML;'):
            if self.execute_script('return grecaptcha.getResponse();') == '':

                if len(self.harvester_manager.response_queue) > 0:

                    self.find_element(By.CLASS_NAME, 'g-recaptcha')
                    value = self.find_element(By.CLASS_NAME, 'g-recaptcha-response').text
                    if value == '' or self.execute_script('return grecaptcha.getResponse();') == '':
                        self.execute_script(f'document.getElementsByClassName("g-recaptcha-response")[0].value = "{self.harvester_manager.response_queue[0]["response"]}";')
                        self.execute_script(f'document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML = "{self.harvester_manager.response_queue[0]["timestamp"]}";')
                        self.harvester_manager.response_queue.pop(0)

        timestamp = self.execute_script(f'return document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML;')

        if timestamp:
            now = datetime.datetime.now()
            timestamp_string = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            delta = now - timestamp_string
            if delta.seconds > 120:
                self.execute_script(f'document.getElementsByClassName("g-recaptcha-response")[0].value = "";')
                self.execute_script(
                    f'document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML = "";')
                self.execute_script(
                    f'document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML = "";')


# Example of using captcha harvester with example Bot class that is receiving captcha responses and using them to submit form.
# NOTE. This example uses 2 Harvester objects, 1 of them uses logging in to Google account and launching extra window with Youtube.

def main():

    url = 'https://www.google.com/recaptcha/api2/demo'
    # Scraping sitekey from url
    sitekey = harvester.Harvester.get_sitekey(url)

    # Creating HarvesterManager object
    harvester_manager = harvester.HarvesterManger()
    # Adding Harvester object to HarvesterManager object with url and sitekey as arguments
    harvester_manager.add_harvester(harvester.Harvester(url=url, sitekey=sitekey))
    # Adding Harvester object to HarvesterManager object with additional arguments to login to Google account and open window with Youtube.
    harvester_manager.add_harvester(harvester.Harvester(url=url, sitekey=sitekey, log_in=True, open_youtube=True))
    # Launching all harvesters
    harvester_manager.start_harvesters()
    # Creating Bot object with HarvesterManager as argument so it can reach its response_queue
    bot = Bot(harvester_manager)
    # Launching Bot
    bot.start(url=url)
    # Creating bot and harvester_manager main_loop threads
    bot_loop_thread = Thread(target=bot.main_loop)
    harvester_manager_loop_thread = Thread(target=harvester_manager.main_loop)
    # Starting threads
    bot_loop_thread.start()
    harvester_manager_loop_thread.start()
    # Joining threads
    bot_loop_thread.join()
    harvester_manager_loop_thread.join()


if __name__ == '__main__':
    main()
