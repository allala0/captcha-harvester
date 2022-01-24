from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os

class Browser(Chrome):

    os.environ['WDM_LOG_LEVEL'] = '0'

    def __init__(self, executable=None, options=None, experimental_options=None):

        self.executable = executable
        self.options = ChromeOptions()

        if options:
            for option in options:
                self.options.add_argument(option)
        if experimental_options:
            for name, value in experimental_options.items():
                self.options.add_experimental_option(name, value)

    def start(self, url: str = None, **kwargs):
        service = Service(self.executable) if self.executable else Service(ChromeDriverManager().install())
        super(Browser, self).__init__(service=service, options=self.options)
        if url:
            self.get(url)

    def is_website_ready(self) -> bool:
        return self.execute_script('return document.readyState;') == 'complete' if self.is_open else False
    @property
    def is_open(self) -> bool:
        try:
            log = self.get_log('driver')
            if log:
                if 'message' in log[0]:
                    if log[0]['message'] == 'Unable to evaluate script: disconnected: not connected to DevTools\n':
                        return False
        except:
            return False
        else:
            return True
