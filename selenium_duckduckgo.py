# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Create ChromeDriver instance
def _get_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome(
        "/Users/ilian/Downloads/explorer/chromedriver_mac64/chromedriver"
    )  # noqa: E501
    return driver


driver = _get_driver()

url = "https://www.psychologytoday.com/us/therapists/ca/oakland"
# Load DuckDuckGo
driver.get(url)

# Find search box element and enter search query
search_box = driver.find_element_by_name("q")
search_box.send_keys("therapists bay area")

# Submit search query
search_box.send_keys(Keys.RETURN)

# Wait for page to load
time.sleep(5)

# Find all therapist results and print them
import IPython

IPython.embed()
results = driver.find_elements_by_xpath("//div[@class='result__url']/a")
for result in results:
    print(result.text)

# Close browser
driver.quit()
