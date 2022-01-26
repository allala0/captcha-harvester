<p align="center"><img src="img/logo.png" width=300;/></p>
<h1 align="center">Captcha Harvester</h1>
<p align="center">Solve captcha beforehand and use them when needed.</p>



## Introduction

### What is captcha harvester?

Captcha harvester is a tool to solve captchas yourself, store them, and evantually use when you need them in your automation software / bot.

### Example usecase

Bot to buy limited products. When your bot is at checkout, you don't have to solve captcha, you can solve it before and inject solved captcha when it needed. It gives you advanatge of extra couple seconds.

### How does captcha harvester work?

Harvester is instance of chromedriver ran with Selenium. Chromedriver opens website you want to harvest captchas on. HTML is changed to blank HTML document with just captcha box in it. Captcha is rendered and user can solve captchas. When captcha is solved by user, captcha response is stored in response queue and captcha box is reseted so user can solve more captchas. When captcha response is needed in your automation software / bot it can be pulled from response queue and used.

There is a HarvesterManager class that is managing all Harvesters, when main_loop is ran, HarvesterManager is executing tick function in all Harvesters in infinite loop, all responses from queues in Harvesters are moved to single queue in HarvesterManager.

## Features

Captcha Harvester supports logging in to your Google account to lower captcha difficulty.
Harvester can run with additional window where Youtube videos will be viewed to make activity on your Google account to lower captcha difficulty. 

## Compatibility

Captcha harvester was tested and working on Windows and Linux.

For now harvester is compatible with reCAPTCHA v2. In the future it will be compatible with reCAPTCHA v3, hCaptcha and others.

## Requirements

- Python 3
- All packages from requirements.txt
- Google Chrome

## Installation

- Download and install Python 3 from <a href="https://www.python.org/downloads/">here</a>.
- Install all packages from requirements.txt. In terminal type: `pip install -r requirements.txt` ( You need to be in same directory as requirements.txt or provide full path to requirements.txt. )
- Install Google Chrome from <a href="https://www.google.com/chrome/">here</a>.

## How to use

- Example code

    - In example.py is shown an example of a simple way to use harvester.
    - In example_bot.py is shown an example of connecting harvester with bot and sending solved captchas to it.

    To run example code just run example.py or example_bot.py with python.
    
    Note that in example_bot.py Harvester is added with additional parameters, there are much more additional parameters ( look in Harvester class ).
    
    Note that you can add as many harvesters as you want ( Limit is only your computer specs ).
    
    Note that there is expiration time for every captcha solved. For reCaptcha v2 expiration time is 120 seconds counted from moment of successful solve end.
