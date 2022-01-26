## Introduction

- What is captcha harvester?

Captcha harvester is a tool to solve captchas yourself, store them, and evantually use them when you need them in your automation software / bot.

- Example usecase

Bot to buy limited products. When your bot is at checkout, you don't have to solve captcha, you can solve it before and inject solved captcha when it needed. It gives you advanatge of extra couple seconds.

## Compatibility

Captcha harvester was tested and working on Windows and Linux.

For now harvester is compatible with reCAPTCHA v2. In the future it will be compatible with reCAPTCHA v3, hCaptcha and others.

## Requirements

- Python 3
- All packages from requirements.txt
- Google Chrome

## Installation

- Download and install Python 3 from <a href="https://www.python.org/downloads/"></a>
- Install all packages from requirements.txt. In terminal type: `pip install -r requirements.txt`
- Install Google Chrome from <a href="https://www.google.com/chrome/"></a>

## How to use

- Example code

  - In example.py is shown an example of a simple way to use harvester.
  - In example_bot.py is shown an example of connecting harvester with bot and sending solved captchas to it.

To run example code just run example.py or example_bot.py with python.

