# Importing local packages
from browser import Browser
# Importing external packages
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import requests
from requests_html import HTML
# Importing standard packages
import pathlib
import random
import os
import datetime
from distutils.dir_util import copy_tree


LOGIN_URL = 'https://accounts.google.com'
LOGGED_URL = 'https://myaccount.google.com'
LOGIN_AUTO_CLOSE_URL = 'https://www.google.com'

YOUTUBE_URL = 'https://www.youtube.com/'
YOUTUBE_VIDEO_URL_PREFIX = 'https://www.youtube.com/watch?v='

CAPTCHA_JS_URL = 'https://www.google.com/recaptcha/api.js'

DEFAULT_CHROME_PATHS = ('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', 'C:/Program Files/Google/Chrome/Application/chrome.exe')


class Harvester(Browser):
    harvester_count = 0

    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pathlib.Path('chrome_profiles/harvester').mkdir(parents=True, exist_ok=True)

    extension_blueprint_path = f'{pathlib.Path().absolute()}/extension'

    def __init__(self, url: str, sitekey: str, proxy: str = None, log_in: bool = False, chrome_executable: str = None, chromedriver_executable: str = None, download_js: bool = True, auto_close_login: bool = True, open_youtube: bool = False, harvester_width: int = 420, harvester_height: int = 600, youtube_width: int = 480, youtube_height: int = 380):
        """
        :param url: Url of website you want to harvest captcha on.
        :param sitekey: Sitekey of website you want to harvest captcha on, can be found in HTML elemement with class "g-recaptcha".
        :param proxy: Proxy in "ip:port" or "ip:port:login:password"
        :param log_in: True if you want to login to your Google account to have easier captchas, false if not.
        :param chrome_executable: Path to chrome.exe that will be used to login to Google, if not provided, all paths from DEFAULT_CHROME_PATHS will be checked for presence of chrome.exe, if not found login process will be skipped.
        :param chromedriver_executable: Path to chrome.exe.
        :param download_js: True: download latest captcha js script, False: use js version stored in code.
        :param auto_close_login: True: Chrome login window automatically closed after login, False: login window is not automatically closed.
        :param width: Width of harvester window.
        :param height: Height of harvester window.
        :param open_youtube: True: open browser with YouTube, where by watching videos you can lower your captcha difficulty.
        :param youtube_width: Width of youtube window.
        :param youtube_height: Height of youtube window.
        """

        self.url = url
        self.sitekey = sitekey
        self.proxy = proxy
        self.log_in = log_in
        self.chrome_executable = chrome_executable
        self.chromedriver_executable = chromedriver_executable
        self.download_js = download_js
        self.auto_close_login = auto_close_login
        self.open_youtube = open_youtube
        self.harvester_width = harvester_width
        self.harvester_height = harvester_height
        self.youtube_width = youtube_width
        self.youtube_height = youtube_height

        self.id = Harvester.harvester_count

        self.profile_path = f'{pathlib.Path().absolute()}/chrome_profiles/harvester/{self.id}'
        self.extension_path = f'{self.profile_path}/extension'
        self.proxy_auth_extension_path = f'{self.profile_path}/proxy_auth_extension'

        self.response_queue = list()
        self.control_element = f'controlElement{random.randint(0, 10 ** 10)}'
        self.is_youtube_setup = False
        self.ticking = False

        Harvester.harvester_count += 1
        pathlib.Path(self.profile_path).mkdir(parents=True, exist_ok=True)
        pathlib.Path(self.proxy_auth_extension_path).mkdir(parents=True, exist_ok=True)
        copy_tree(self.extension_blueprint_path, self.extension_path)

        chrome_options = [
            # f'--app={self.url}',
            # Initially opening google to then redirect to harvest website, so when using proxy, the login popup will disappear
            f'--app=http://www.google.com/',
            f'--window-size={self.harvester_width},{self.harvester_height}',
            f'--user-data-dir={self.profile_path}',
            '--disable-infobars',
            '--disable-menubar',
            '--disable-toolbar',
            '--mute-audio',
            '--log-level=3',
            "--disable-notifications",
        ]
        chrome_experimental_options = {
            'prefs': {'profile': {'exit_type': 'Normal'}}
        }

        self.use_proxy_extension = False

        if proxy:
            if len(proxy.split(':')) >= 4:

                self.use_proxy_extension = True
                chrome_options.append('--proxy-server=' + proxy.split(':')[0] + ':' + proxy.split(':')[1])
                manifest_json, background_js = self.get_proxy_auth_extension(proxy)

                with open(self.proxy_auth_extension_path + '/manifest.json', 'w') as file:
                    file.write(manifest_json)

                with open(self.proxy_auth_extension_path + '/background.js', 'w') as file:
                    file.write(background_js)

                chrome_options.append(f'--load-extension={self.proxy_auth_extension_path}')
            else:
                chrome_options.append('--proxy-server=' + proxy)

        super(Harvester, self).__init__(executable=self.chromedriver_executable, options=chrome_options, experimental_options=chrome_experimental_options)

        if self.log_in:
            self.start = self.login_decorator(self.start)

        self.ip_done = False

    def login_decorator(self, func):
        def wrapper(*args, **kwargs):
            self.login()
            rv = func(*args, **kwargs)
            return rv
        return wrapper

    def login(self) -> None:

        if self.auto_close_login:
            start_url = LOGIN_AUTO_CLOSE_URL
            # This JS script is opening new window and closing window that was open before to get around the Chrome rule "Scripts may close only the windows that were opened by them.", so after user log in to Google, window can be closed automatically.
            content_js = f'if(document.location.href.includes("{start_url}")){{window.open("{LOGIN_URL}", "", "scrollbars=yes,status=yes,menubar=no,toolbar=no");window.close();}}if(document.location.href.includes("{LOGGED_URL}")){{window.close();}}'
        else:
            start_url = LOGIN_URL
            content_js = ''

        with open(f'{self.extension_path}/content.js', 'w') as f:
            f.write(content_js)

        chrome_args = [
            f'--app={start_url}',
            f'--window-size={self.harvester_width},{self.harvester_height}',
            f'--user-data-dir="{self.profile_path}"',
            '--disable-infobars',
            '--disable-menubar',
            '--disable-toolbar',
            '--log-level=3',
            f'--load-extension="{self.extension_path}"',
        ]

        if self.proxy:
            if self.use_proxy_extension:
                chrome_args.append('--proxy-server=' + self.proxy.split(':')[0] + ':' + self.proxy.split(':')[1])
                chrome_args.append(f'--load-extension="{self.extension_path}","{self.proxy_auth_extension_path}"')
            else:
                chrome_args.append('--proxy-server=' + self.proxy)

        command = ''
        for arg in chrome_args:
            command += f' {arg}'

        chrome_paths = (self.chrome_executable,) + DEFAULT_CHROME_PATHS if self.chrome_executable else DEFAULT_CHROME_PATHS

        for chrome_path in chrome_paths:
            if os.path.isfile(chrome_path):
                command = f'"{chrome_path}"' + command
                os.popen(command).close()
                break

    def setup(self) -> None:
        if not self.is_open:
            return
        if self.is_set:
            return

        captcha_js = "(function(){var w=window,C='___grecaptcha_cfg',cfg=w[C]=w[C]||{},N='grecaptcha';var gr=w[N]=w[N]||{};gr.ready=gr.ready||function(f){(cfg['fns']=cfg['fns']||[]).push(f);};w['__recaptcha_api']='https://www.google.com/recaptcha/api2/';(cfg['render']=cfg['render']||[]).push('onload');w['__google_recaptcha_client']=true;var d=document,po=d.createElement('script');po.type='text/javascript';po.async=true;po.src='https://www.gstatic.com/recaptcha/releases/-FJgYf1d3dZ_QPcZP7bd85hc/recaptcha__en.js';po.crossOrigin='anonymous';po.integrity='sha384-w2lIrXdcsRgXIRsq1Y2C2rGrB0G3iE5CLYGxlFzUAbix3gGjUFYcQavOqddMOp1u';var e=d.querySelector('script[nonce]'),n=e&&(e['nonce']||e.getAttribute('nonce'));if(n){po.setAttribute('nonce',n);}var s=d.getElementsByTagName('script')[0];s.parentNode.insertBefore(po, s);})();"

        harvester_title = f'Harvester {self.id}'
        if self.proxy:
            if self.use_proxy_extension:
                harvester_title += f' (proxy: "{self.proxy.split(":")[0]}:{self.proxy.split(":")[1]}")'
            else:
                harvester_title += f' (proxy: "{self.proxy}")'
        harvester_icon = 'img/icon.png'
        harvester_html = f'<html><head><link rel="icon" href="{harvester_icon}"><title>{harvester_title}</title><script src="{CAPTCHA_JS_URL}" async defer></script></head><body><div class="{self.control_element}"></div><div id="container"><div id="g-recaptcha" class="g-recaptcha" data-sitekey="{self.sitekey}"></div></div></body></html>'
        harvester_loop_script = 'var tick = function(){var divs = document.querySelector("body").children;for(i=0; i<divs.length; i++){divs[i].style.left = 0;divs[i].style.top = 0;}setTimeout(tick, 100);};tick();'
        harvester_container = 'document.getElementById("container")'

        scripts = (
            f"document.documentElement.innerHTML = '{harvester_html}';",
            f'{harvester_container}.style.width = "305px";',
            f'{harvester_container}.style.marginLeft = "auto";',
            f'{harvester_container}.style.marginRight = "auto";',
            f'{harvester_container}.style.marginTop = "242px";',
            harvester_loop_script,
        )

        self.get(self.url) if self.current_url != self.url else None

        for script in scripts:
            self.execute_script(script)

        if self.download_js:
            try:
                captcha_js = requests.get(CAPTCHA_JS_URL).text
            except requests.RequestException:
                pass

        self.execute_script(captcha_js)

    def get_response(self) -> dict:
        if not self.is_open:
            return dict()
        response = self.execute_script('return grecaptcha.getResponse();')
        return {'timestamp': datetime.datetime.now(), 'response': response} if response else dict()

    def pull_response_queue(self) -> list:
        response_queue, self.response_queue = self.response_queue, list()
        return response_queue

    def pull_response(self) -> dict:
        return self.response_queue.pop(0) if self.response_queue else dict()

    def reset_harvester(self) -> None:
        if not self.is_open:
            return
        
        self.execute_script('grecaptcha.reset();')

    def window_size_check(self) -> None:
        if not self.is_open:
            return

        harvester_size = self.get_window_size()
        if harvester_size['width'] != self.harvester_width or harvester_size['height'] != self.harvester_height:
            self.set_window_size(self.harvester_width, self.harvester_height)

    def response_check(self) -> None:
        response = self.get_response()
        if response:
            self.reset_harvester()
            self.response_queue.append(response)

    def youtube_setup(self) -> None:
        if not self.is_open or self.is_youtube_setup or not self.open_youtube:
            return

        self.execute_script(f"window.open('{YOUTUBE_URL}', '_blank', 'toolbar=no').resizeTo({self.youtube_width}, {self.youtube_height});")

        if len(self.window_handles) > 1:
            self.switch_to.window(self.window_handles[1])
            for link in self.find_elements(By.TAG_NAME, 'a'):
                if not link.get_attribute('href'):
                    continue
                if YOUTUBE_VIDEO_URL_PREFIX in link.get_attribute('href'):
                    self.get(link.get_attribute('href'))
                    self.refresh()
                    break
            self.is_youtube_setup = True

        self.switch_to.window(self.window_handles[0])

    def tick(self) -> None:
        self.ticking = True
        # This try except to be upgraded...
        try:
            # self.show_ip()
            self.setup()
            self.youtube_setup()
            self.response_check()
            self.window_size_check()
        except WebDriverException:
            print('Some Selenium error (harvester).')

        self.ticking = False

    @property
    def is_set(self) -> bool:
        try:
            return True if self.find_elements(By.CLASS_NAME, self.control_element) else False
        except:
            return False

    @staticmethod
    def get_sitekey(url: str) -> str:
        # NOTE. In HTML of provided website need to be an element with "g-recaptcha" class and "data-sitekey" tag or there need to be JS script where sitekey is set like: 'sitekey': 'example_sitekey'
        try:
            response = requests.get(url)
            if not response.ok:
                return
        except requests.exceptions.BaseHTTPError:
            return
        else:
            html = HTML(html=response.text)
            captcha_element = html.find('.g-recaptcha')
            sitekey = captcha_element[0].attrs.get('data-sitekey') if captcha_element else None
            if sitekey:
                return sitekey
            html_formated = ''.join(response.text.split())
            sitekey_index = html_formated.find('sitekey')
            return html_formated[sitekey_index + 10:sitekey_index + 50] if sitekey_index != -1 and len(html_formated) > sitekey_index + 50 else None

    @staticmethod
    def get_proxy_auth_extension(proxy: str) -> tuple:
        proxy = proxy.split(':')
        manifest_json = """{
    "manifest_version": 2,
    "version": "0.1",
    "name": "Chrome Proxy",
    "permissions": [
        "tabs",
        "unlimitedStorage",
        "proxy",
        "webRequestBlocking",
        "storage",
        "<all_urls>",
        "webRequest"
    ],
    "background": {
        "scripts": ["background.js"]
    }
}
        """
        background_js = """

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
        """ % (proxy[2], proxy[3])
        return manifest_json, background_js
