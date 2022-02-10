# Importing external packages
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# Importing standard packages
import os

DRIVER_CLOSED_MESSAGE = 'Unable to evaluate script: disconnected: not connected to DevTools\n'

# Setting environment variable to disable webdriver_manager log.
os.environ['WDM_LOG_LEVEL'] = '0'


class Browser(Chrome):

    def __init__(self, executable: str = None, options: list = None, experimental_options: dict = None):
        self.executable = executable
        if executable:
            if not os.path.isfile(executable):
                self.executable = None

        self.options = ChromeOptions()

        if options:
            for option in options:
                self.options.add_argument(option)
        self.options.add_argument("--lang=en-US")
        if experimental_options:
            for name, value in experimental_options.items():
                self.options.add_experimental_option(name, value)

    def start(self, url: str = None) -> None:
        service = Service(self.executable) if self.executable else Service(ChromeDriverManager().install())
        super(Browser, self).__init__(service=service, options=self.options)
        if url:
            self.get(url)

    @property
    def is_website_ready(self) -> bool:
        return self.execute_script('return document.readyState;') == 'complete'

    @property
    def is_open(self) -> bool:
        log = self.get_log('driver')
        if not log:
            return True
        if log[0].get('message') == DRIVER_CLOSED_MESSAGE:
            return False
        return True
