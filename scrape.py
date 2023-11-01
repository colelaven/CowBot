from utils import log
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import urllib
import time
from PIL import Image

# async def scrapeRank(username):
#     URL = F"https://rocketleague.tracker.network/rocket-league/profile/epic/{urllib.parse.quote(username)}/overview"
#     options = Options()
#     options.add_argument("--headless=new")
#     DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
#     service = Service(executable_path=DRIVER_PATH)
#     driver = webdriver.Chrome(service=service, options=options)
#     print("driver created")
#     driver.get(URL)
#     print("got page")
#     try:
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "value")))
#         print("page loaded")
#         ones_mmr = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div/main/div[3]/div[3]/div[1]/div/div/div[1]/div[2]/table/tbody/tr[2]/td[3]/div/div[2]/div[1]/div").text
#         twos_mmr = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div/main/div[3]/div[3]/div[1]/div/div/div[1]/div[2]/table/tbody/tr[3]/td[3]/div/div[2]/div[1]/div").text
#         threes_mmr = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div/main/div[3]/div[3]/div[1]/div/div/div[1]/div[2]/table/tbody/tr[4]/td[3]/div/div[2]/div[1]/div").text
#         response = F"**__Ranks For {username}__**\n1v1 MMR: {ones_mmr}\n2v2 MMR: {twos_mmr}\n3v3 MMR: {threes_mmr}"
#         print("got mmrs:")
#         print(response)
#         return response
#     except:
#         print("error")
#         return "Error Scraping RL Tracker"
#     finally:
#         driver.quit()

# def scrapeRank(username):
#     URL = F"https://rlstats.net/profile/Epic/{urllib.parse.quote(username)}"
#     DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
    
#     options = Options()
#     options.add_argument("--headless=new")
    
#     service = Service(executable_path=DRIVER_PATH)
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.get(URL)
#     print("got page")
#     try:
#         time.sleep(5)
#         print("done sleeping")
#         WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='Widget containing a Cloudflare security challenge']")))
#         WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
#         print("got past cloudflare")
#         time.sleep(5)
#         webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
#         webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
#         element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "block-skills")))
#         print("page loaded")
#         return "success"
#     except Exception as e:
#         log(f"Error scraping/cropping for {username}: {type(e)}\n{e}")
#         return f"Error fetching rank for {username}, did you input an Epic Games username?"
#     finally:
#         driver.quit()

async def scrapeRankScreenshot(username):
    URL = F"https://rocketleague.tracker.network/rocket-league/profile/epic/{urllib.parse.quote(username)}/overview"
    DRIVER_PATH = "/usr/lib/chromium-browser/chromedriver"
    SCREENSHOT_PATH = "/home/cole/repos/CowBot/screenshots/rank.png"
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=940,940")
    options.add_argument("--hide-scrollbars")
    
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "value")))
        
        driver.execute_script("window.scrollTo(0, 1410)")
        driver.save_screenshot(SCREENSHOT_PATH)

        elements = driver.find_elements(By.CLASS_NAME, 'playlist')
        playlists = [element.text for element in elements]
        print(playlists)

        fullScreenshot = Image.open(SCREENSHOT_PATH)
        if playlists[0] == "Un-Ranked":
            cropped = fullScreenshot.crop((0,266,860,418))
        else:
            cropped = fullScreenshot.crop((0,216,860,367))
        
        cropped.save(SCREENSHOT_PATH)

        return "success"
    except:
        log(f"Error scraping/cropping for {username}")
        return f"Error fetching rank for {username}, did you input an Epic Games username?"
    finally:
        driver.quit()

# scrapeRankScreenshot("claven.")
