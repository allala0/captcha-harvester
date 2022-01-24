# Importing local packages
from browser import Browser
from tools import mkdir
# Importing external packages
from selenium.webdriver.common.by import By
import requests
# Importing standard packages
import pathlib
import random
import os
import datetime
from distutils.dir_util import copy_tree


class Harvester(Browser):
    harvester_count = 0

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    mkdir('chrome_profiles')
    mkdir('chrome_profiles/harvester')

    def __init__(self, url: str, sitekey: str, log_in: bool = False, chrome_executable: str = None, chromedriver_executable: str = None, download_js: bool = False, auto_close_login: bool = True, open_youtube: bool = False):
        """
        :param url: Url of website you want to harvest captcha on.
        :param sitekey: Sitekey of website you want to harvest captcha on, can be found in elemement with class "g-recaptcha".
        :param log_in: True if you want to login to your Google account to have easier captchas, false if not.
        :param chrome_executable: Path to chrome.exe.
        :param chromedriver_executable: Path to chrome.exe.
        :param download_js: True: download latest captcha js script, False: use js version stored in code.
        :param auto_close_login: True: Chrome login window automaticly closed after login, False: Login window is not automatically closed.
        :param open_youtube: True: open browser with YouTube, where by watching videos you can lower your captcha difficulty, login need to be True
        """

        self.url = url
        self.sitekey = sitekey
        self.log_in = log_in
        self.chrome_executable = chrome_executable
        self.chromedriver_executable = chromedriver_executable
        self.download_js = download_js
        self.auto_close_login = auto_close_login
        self.open_youtube = open_youtube

        self.id = Harvester.harvester_count

        self.login_url = 'https://accounts.google.com'
        self.logged_url = 'https://myaccount.google.com'

        self.width = 420
        self.height = 600

        self.profile_path = f'{pathlib.Path().absolute()}\\chrome_profiles\\harvester\\{self.id}'
        self.extension_blueprint_path = f"{pathlib.Path().absolute()}\\extension"
        self.extension_path = f"{self.profile_path}\\extension"

        self.to_open = ['https://www.youtube.com'] if self.open_youtube else []
        self.control_element = f'controlElement{random.randint(0, 10 ** 10)}'
        self.is_youtube_setup = False
        self.ticking = False

        self.response_queue = list()

        Harvester.harvester_count += 1
        mkdir(self.profile_path)
        copy_tree(self.extension_blueprint_path, f'{self.profile_path}\\extension')

        if self.log_in:
            self.decorate_start_with_login()


        options = (
            f'--app={self.url}',
            f'--window-size={self.width},{self.height}',
            f'--user-data-dir={self.profile_path}',
            '--disable-infobars',
            '--disable-menubar',
            '--disable-toolbar',
            '--mute-audio',
        )
        experimental_options = {
            'prefs': {'profile': {'exit_type': 'Normal'}}
        }

        super(Harvester, self).__init__(executable=chromedriver_executable, options=options, experimental_options=experimental_options)

    def decorate_start_with_login(self) -> None:
        def login_decorator(func):
            def wrapper(*args, **kwargs):
                self.login()
                rv = func(*args, **kwargs)
                return rv

            return wrapper

        self.start = login_decorator(self.start)

    def login(self) -> None:

        if self.auto_close_login:
            start_url = 'https://www.google.com'
            content_js = f'if(document.location.href.includes("{start_url}")){{window.open("{self.login_url}", "", "scrollbars=yes,status=yes,menubar=no,toolbar=no");window.close();}}if(document.location.href.includes("{self.logged_url}")){{window.close();}}'
        else:
            start_url = self.login_url
            content_js = ''

        args = (
            f'--app={start_url}',
            f'--window-size={self.width},{self.height}',
            f'--user-data-dir="{self.profile_path}"',
            '--disable-infobars',
            '--disable-menubar',
            '--disable-toolbar',
            f'--load-extension="{self.extension_path}"',
        )

        with open(f'{self.extension_path}\\content.js', 'w') as f:
            f.write(content_js)

        if self.chrome_executable is None:
            paths = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe', 'C:\Program Files\Google\Chrome\Application\chrome.exe'
        else:
            paths = self.chrome_executable

        for path in paths:
            if os.path.isfile(path):
                command = f'"{path}"'
                for arg in args:
                    command += f' {arg}'
                os.popen(command).close()
                break

    def setup(self) -> None:
        if self.is_open and not self.is_set():
            title = f'(Instance {self.id}) Captcha Harvester'
            js_url = 'https://www.google.com/recaptcha/api.js'
            js = "(function(){var w=window,C='___grecaptcha_cfg',cfg=w[C]=w[C]||{},N='grecaptcha';var gr=w[N]=w[N]||{};gr.ready=gr.ready||function(f){(cfg['fns']=cfg['fns']||[]).push(f);};w['__recaptcha_api']='https://www.google.com/recaptcha/api2/';(cfg['render']=cfg['render']||[]).push('onload');w['__google_recaptcha_client']=true;var d=document,po=d.createElement('script');po.type='text/javascript';po.async=true;po.src='https://www.gstatic.com/recaptcha/releases/-FJgYf1d3dZ_QPcZP7bd85hc/recaptcha__en.js';po.crossOrigin='anonymous';po.integrity='sha384-w2lIrXdcsRgXIRsq1Y2C2rGrB0G3iE5CLYGxlFzUAbix3gGjUFYcQavOqddMOp1u';var e=d.querySelector('script[nonce]'),n=e&&(e['nonce']||e.getAttribute('nonce'));if(n){po.setAttribute('nonce',n);}var s=d.getElementsByTagName('script')[0];s.parentNode.insertBefore(po, s);})();"
            icon = 'img/icon.png'
            html = f'<html><head><link rel="icon" href="{icon}"><title>{title}</title><script src="{js_url}" async defer></script></head><body><div class="{self.control_element}"></div><div id="container"><div id="g-recaptcha" class="g-recaptcha" data-sitekey="{self.sitekey}"></div></div></body></html>'

            container = 'document.getElementById("container")'

            scripts = (
                f"document.documentElement.innerHTML = '{html}';",
                f'{container}.style.width = "305px";',
                f'{container}.style.marginLeft = "auto";',
                f'{container}.style.marginRight = "auto";',
                f'{container}.style.marginTop = "242px";',
                'var tick = function(){var divs = document.querySelector("body").children;for(i=0; i<divs.length; i++){divs[i].style.left = 0;divs[i].style.top = 0;}setTimeout(tick, 100);};tick();',
            )

            try:
                self.get(self.url)
                for script in scripts:
                    self.execute_script(script)
            except:
                print('err1')
            else:
                if self.download_js:
                    try:
                        js = requests.get(js_url).text
                    except requests.RequestException as e:
                        print(e)
                try:
                    self.execute_script(js)
                except:
                    print('err2')

    def get_response(self) -> dict:
        if self.is_open:
            try:
                r = self.execute_script('return grecaptcha.getResponse();')
                return {'timestamp': datetime.datetime.now(), 'response': r} if r else dict()
            except:
                return dict()
        else:
            return dict()

    def pull_response_queue(self) -> list:
        response_queue, self.response_queue = self.response_queue, list()
        return response_queue

    def pull_response(self) -> dict:
        return self.response_queue.pop(0) if self.response_queue else dict()

    def is_set(self) -> bool:
        if self.is_open:
            try:
                return True if self.find_elements(By.CLASS_NAME, self.control_element) else False
            except:
                return False
        else:
            return False

    def reset(self) -> None:
        if self.is_open:
            try:
                self.execute_script('grecaptcha.reset();')
            except:
                print('err4')

    def window_size_check(self) -> None:
        if self.is_open:
            try:
                size = self.get_window_size()
                if size['width'] != self.width or size['height'] != self.height:
                    self.set_window_size(self.width, self.height)
            except:
                print('err5')

    def response_check(self) -> None:
        response = self.get_response()
        if response:
            self.reset()
            self.response_queue.append(response)

    def youtube_setup(self) -> None:
        try:
            if self.to_open:
                to_open, self.to_open = self.to_open, list()
                for el in to_open:
                    try:
                        self.execute_script(
                            f"window.open('{el}', '_blank', 'height=200,scrollbars=yes,status=yes,menubar=no,toolbar=no').resizeTo(480, 380);")
                    except:
                        self.to_open.append(el)

                if len(self.window_handles) > 1 and not self.is_youtube_setup:
                    self.switch_to.window(self.window_handles[1])
                    if self.current_url == 'https://www.youtube.com/':
                        links = self.find_elements(By.TAG_NAME, 'a')
                        for link in links:
                            if link.get_attribute('href'):
                                if 'https://www.youtube.com/watch?v=' in link.get_attribute('href'):
                                    self.get(link.get_attribute('href'))
                                    self.refresh()
                                    break
                    self.is_youtube_setup = True
        finally:
            try:
                self.switch_to.window(self.window_handles[0])
            except:
                pass

    def tick(self) -> None:
        self.ticking = True
        if self.is_open:
            self.setup()
            self.youtube_setup()
            self.response_check()
            self.window_size_check()

        self.ticking = False
