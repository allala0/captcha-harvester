from harvester import Harvester

import tools

import time
from threading import Thread


class HarvesterManger:
    def __init__(self):
        self.harvesters = list()
        self.response_queue = list()
        self.looping = False
        self.delay = 0.2

    def add_harvester(self, harvester: Harvester):
        self.harvesters.append(harvester)

    def start_harvesters(self, use_threads=True):
        if use_threads:
            tools.thread_loop(*[harvester.start for harvester in self.harvesters])
        else:
            for harvester in self.harvesters:
                harvester.start()

    def main_loop(self):
        if not self.looping:
            self.looping = True
            while self.looping:
                self.tick()
                time.sleep(self.delay)

    def tick(self):
        self.get_responses()
        for harvester in self.harvesters:
            if not harvester.ticking:
                Thread(target=harvester.tick).start()

    def get_responses(self):
        for harvester in self.harvesters:
            if harvester.response_queue:
                self.response_queue += harvester.response_queue
                harvester.response_queue = list()

    # def pull_response(self):
    #     responses = self.get_responses()
    #     if responses:
    #         response = sorted(responses, key=lambda r: r[0])[0]
    #         for harvester in self.harvesters:
    #             for i, r in enumerate(harvester.response_queue):
    #                 if r == response:
    #                     harvester.response_queue.pop(i)
    #         print(response)

