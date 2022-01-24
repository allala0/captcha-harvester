# Importing local packages
from harvester import Harvester
# Importing external packages
# Importing standard packages
import time
from threading import Thread
import datetime


class HarvesterManger:
    def __init__(self, delay: int = 0.1, response_callback=None):
        """
        HarvesterManager manages Harvester class objects.
        :param delay: Delay in seconds between main_loop ticks.
        :param response_callback: If callback function provided, this function will be called with capthcha response as param everytime CaptchaHarvester executes method "pull_responses_from_harvesters", if not provided responses will be added to self.response_queue.
        """
        self.delay = delay
        self.response_callback = response_callback

        self.harvesters = list()
        self.response_queue = list()
        self.looping = False

    def add_harvester(self, harvester: Harvester) -> None:
        self.harvesters.append(harvester)

    def start_harvesters(self, use_threads: bool = True) -> None:
        if use_threads:
            threads = list()
            for harvester in self.harvesters:
                threads.append(Thread(target=harvester.start))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        else:
            for harvester in self.harvesters:
                harvester.start()

    def main_loop(self) -> None:
        if not self.looping:
            self.looping = True
            while self.looping:
                self.tick()
                time.sleep(self.delay)

    def tick(self) -> None:
        self.pull_responses_from_harvesters()
        self.response_queue_check()
        for harvester in self.harvesters:
            if not harvester.ticking:
                Thread(target=harvester.tick).start()

    def response_queue_check(self) -> None:
        self.response_queue = list(filter(lambda x: (datetime.datetime.now() - x['timestamp']).seconds < 120, self.response_queue))

    def pull_responses_from_harvesters(self):
        for harvester in self.harvesters:
            if self.response_callback:
                for response in harvester.pull_response_queue():
                    self.response_callback(response)
            else:
                self.response_queue += harvester.pull_response_queue()

