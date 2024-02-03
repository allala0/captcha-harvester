import harvester

# Simple example of using captcha harvester with one Harvester and printing captcha responses to console.

def main():
    url = 'https://www.google.com/recaptcha/api2/demo'
    # Scraping sitekey from url
    sitekey = harvester.Harvester.get_sitekey(url)

    # Creating HarvesterManager object with additional argument response_callback which is function,
    # that will be called everytime HarvesterManager pull captcha response from Harvseter ( after user solve captcha )
    harvester_manager = harvester.HarvesterManger(response_callback=lambda x: print(x['response']))
    # Adding Harvester object to HarvesterManager object with url and sitekey as arguments
    harvester_manager.add_harvester(harvester.Harvester(url, sitekey))
    # Launching all harvesters
    harvester_manager.start_harvesters()
    # Starting main_loop inside HarvesterManager object, that will manage all Harvesters
    harvester_manager.main_loop()


if __name__ == '__main__':
    main()
