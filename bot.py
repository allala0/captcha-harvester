from browser import Browser
from harvester_manager import HarvesterManger
from harvester import Harvester
import time
import datetime
from threading import Thread
from selenium.webdriver.common.by import By
import random
from selenium.common.exceptions import WebDriverException


class Bot(Browser):
    def __init__(self, url, sitekey, delay=0.2):

        super(Bot, self).__init__()

        self.url = url
        self.sitekey = sitekey
        self.delay = delay
        self.control_element = f'controlElement{random.randint(0, 10 ** 10)}'

        self.looping = False

        self.harvester_manager = HarvesterManger()
        self.harvester_manager.add_harvester(Harvester(url=url, sitekey=sitekey))
        self.harvester_manager.start_harvesters()

    def run_loops(self):

        bot_loop_thread = Thread(target=self.main_loop)
        harvester_manager_loop_thread = Thread(target=self.harvester_manager.main_loop)

        bot_loop_thread.start()
        harvester_manager_loop_thread.start()

        bot_loop_thread.join()
        harvester_manager_loop_thread.join()

        return bot_loop_thread, harvester_manager_loop_thread

    def main_loop(self) -> None:
        """
        :return: None
        """
        if not self.looping:
            self.looping = True
            while self.looping:
                try:
                    inject_list = [
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
                    ]

                    if not self.execute_script(f'return document.getElementsByClassName("{self.control_element}")'):
                        for inject_html in inject_list:
                            self.execute_script(inject_html)

                    if self.execute_script('return grecaptcha.getResponse();') == '':

                        self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].style.cursor = "pointer"')

                        self.execute_script(f'document.getElementsByClassName("{self.control_element}")[0].style.border = "2px solid #333"')
                        self.execute_script(f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.backgroundColor = \'#333\';',)
                        self.execute_script(f'document.getElementsByClassName("description_{self.control_element}")[0].innerHTML = "Captchas harvested: {len(self.harvester_manager.response_queue)}"')
                        if self.execute_script(f'return document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML;'):
                            self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Waiting for captcha"')
                        else:
                            self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Click to inject captcha"')
                    else:
                        now = datetime.datetime.now()
                        t = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                        delta = now - t
                        self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].value = "Captha injected"')
                        self.execute_script(f'document.getElementsByClassName("button_{self.control_element}")[0].style.cursor = "default"')
                        self.execute_script(f'document.getElementsByClassName("description_{self.control_element}")[0].innerHTML = "Captha expires in {120 - delta.seconds} seconds"')
                        self.execute_script(f'document.getElementsByClassName("{self.control_element}")[0].style.border = "2px solid green"')
                        self.execute_script(f'document.getElementsByClassName(\'button_{self.control_element}\')[0].style.backgroundColor = \'green\';',)



                    if self.execute_script(f'return document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML;'):
                        if self.execute_script('return grecaptcha.getResponse();') == '':

                            if len(self.harvester_manager.response_queue) > 0:

                                self.find_element(By.CLASS_NAME, 'g-recaptcha')
                                value = self.find_element(By.CLASS_NAME, 'g-recaptcha-response').text
                                if value == '' or self.execute_script('return grecaptcha.getResponse();') == '':
                                    self.execute_script(f'document.getElementsByClassName("g-recaptcha-response")[0].value = "{self.harvester_manager.response_queue[0][1]}";')
                                    self.execute_script(f'document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML = "{self.harvester_manager.response_queue[0][0]}";')
                                    self.harvester_manager.response_queue.pop(0)


                    timestamp = self.execute_script(f'return document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML;')

                    if timestamp:
                        now = datetime.datetime.now()
                        t = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                        delta = now - t
                        if delta.seconds > 120:
                            self.execute_script(f'document.getElementsByClassName("g-recaptcha-response")[0].value = "";')
                            self.execute_script(f'document.getElementsByClassName("timestamp_{self.control_element}")[0].innerHTML = "";')
                            self.execute_script(f'document.getElementsByClassName("clicked_{self.control_element}")[0].innerHTML = "";')

                except WebDriverException:
                    pass

                time.sleep(self.delay)