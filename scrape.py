from utils import log
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
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
        
        fullScreenshot = Image.open(SCREENSHOT_PATH)
        cropped = fullScreenshot.crop((0,182,860,423))
        cropped.save(SCREENSHOT_PATH)
        return "success"
    except:
        log(f"Error scraping/cropping for {username}")
        return f"Error fetching rank for {username}, did you input an Epic Games username?"
    finally:
        driver.quit()
