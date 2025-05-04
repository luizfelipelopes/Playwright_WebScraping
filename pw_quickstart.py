from playwright.sync_api import sync_playwright
from urllib.request import urlretrieve

# initiallize playwright
pw = sync_playwright().start()
# create Firefox browser object
browser = pw.firefox.launch(
    # uncomment the lines below if you're using a web driver
    headless=False 
    # slow_mo=2000
)

# create new browser tab
page = browser.new_page()
# navigate to web page
page.goto("http://arxiv.org/search")

page.get_by_placeholder("Search term...").fill("neural network")

page.get_by_role("button").get_by_text(
    "Search").nth(1).click()

links = page.locator(
    "xpath=//a[contains(@href, 'arxiv.org/pdf')]"
).all()

for link in links:
    url = link.get_attribute("href")
    urlretrieve(url, "data/" + url[-5:] + ".pdf")

    # //*[@id="main-container"]/div[2]/ol/li[1]/div/p/span/a[1]

# web page details and source code
# print(page.content())
# print(page.title())
# page.screenshot(path="example.png")

browser.close()
