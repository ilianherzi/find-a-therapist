from typing_extensions import TypeAlias
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import requests
import re

PSWRD = os.environ["LINKEDIN_PASSWORD"]
SEARCH_QUERY = "site:linkedin.com/in/ AND 'therapist' AND ~california "
NUM_SCROLLS = 5
SEARCH_URI = "https://www.linkedin.com"
USERNAME_WID = "session_key"
PASSWORD_WID = "session_password"
EMAIL = "bitwisetarzan@gmail.com"
SEARCH_ENGINE_URI = "https://google.com"
TIME = 2
UriType: TypeAlias = str
EmailType: TypeAlias = str

# pylint: disable=missing-function-docstring,missing-return-docstring
def _get_driver() -> webdriver.Chrome:
    driver = webdriver.Chrome(
        "/Users/ilian/Downloads/explorer/chromedriver_mac64/chromedriver"
    )  # noqa: E501
    return driver


def find_linkedin_uris(driver: webdriver.Chrome) -> "list[UriType]":
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);",
    )
    for i in range(NUM_SCROLLS):
        print(i)
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight + 500);",
        )
        try:
            welem = EC.element_to_be_clickable((By.CLASS_NAME, "GNJvt"))(driver)
            welem.click()
        except Exception as e:
            print("Did not find Load More button")
            sleep(TIME)
            continue
        sleep(TIME)

    links = driver.find_elements_by_xpath("//a[@href]")
    linkedin_urls = []
    for link in links:
        if "linkedin" in link.text:
            linkedin_urls.append(link.get_attribute("href"))
    return linkedin_urls


def extract_email_from_linkedin_uris(
    linkedin_urls: "list[UriType]",
) -> "list[EmailType]":
    pass


class LinkedIn:
    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 OPR/67.0.3575.97"
        }

    def login(self, email, password):
        try:
            sc = self.s.get("https://www.linkedin.com/login", headers=self.headers).text
        except:
            return False
        csrfToken = sc.split('csrfToken" value="')[1].split('"')[0]
        sid = sc.split('sIdString" value="')[1].split('"')[0]
        pins = sc.split('pageInstance" value="')[1].split('"')[0]
        lcsrf = sc.split('loginCsrfParam" value="')[1].split('"')[0]
        data = {
            "csrfToken": csrfToken,
            "session_key": email,
            "ac": "2",
            "sIdString": sid,
            "parentPageKey": "d_checkpoint_lg_consumerLogin",
            "pageInstance": pins,
            "trk": "public_profile_nav-header-signin",
            "authUUID": "",
            "session_redirect": "https://www.linkedin.com/feed/",
            "loginCsrfParam": lcsrf,
            "fp_data": "default",
            "_d": "d",
            "showGoogleOneTapLogin": "true",
            "controlId": "d_checkpoint_lg_consumerLogin-login_submit_button",
            "session_password": password,
            "loginFlow": "REMEMBER_ME_OPTIN",
        }
        try:
            after_login = self.s.post(
                "https://www.linkedin.com/checkpoint/lg/login-submit",
                headers=self.headers,
                data=data,
            ).text
        except:
            return False
        is_logged_in = after_login.split("<title>")[1].split("</title>")[0]
        if is_logged_in == "LinkedIn":
            return True
        else:
            return False

    def bulkScan(self, profiles):
        all_emails = []
        for profile in profiles:
            profile = profile + "/detail/contact-info/"
            sc = self.s.get(profile, headers=self.headers, allow_redirects=True).text
            emails_found = re.findall("[a-zA-Z0-9\.\-\_i]+@[\w.]+", sc)
            all_emails.extend(emails_found)
        return all_emails

    def singleScan(self, profile):
        profile = profile + "/overlay/contact-info/"
        sc = self.s.get(profile, headers=self.headers, allow_redirects=True).text
        emails_found = re.findall("[a-zA-Z0-9\.\-\_i]+@[\w.]+", sc)
        return emails_found


def run() -> None:
    # Sign into linkedin
    driver = _get_driver()
    driver.get(SEARCH_URI)
    username = driver.find_element(By.ID, USERNAME_WID)
    username.send_keys(EMAIL)
    password = driver.find_element(By.ID, PASSWORD_WID)
    password.send_keys(PSWRD)
    log_in_button = driver.find_element_by_css_selector(
        "[data-id='sign-in-form__submit-btn']"
    )
    log_in_button.click()
    sleep(TIME)

    # new tab
    driver.find_element_by_tag_name("body").send_keys(Keys.COMMAND + "t")
    driver.get(SEARCH_ENGINE_URI)
    search_query = driver.find_element_by_name("q")
    search_query.send_keys(SEARCH_QUERY)
    search_query.send_keys(Keys.RETURN)
    sleep(TIME)

    # search linkedin
    linkedin_urls = find_linkedin_uris(driver)
    linkedin_session = LinkedIn()
    linkedin_session.login(EMAIL, PSWRD)
    import IPython

    IPython.embed()
    with open(
        "/Users/ilian/Downloads/therapists_selenium.csv",
        "w",
        encoding="utf8",
    ) as f:  # noqa: C0103
        f.write("\n".join(linkedin_urls))

    driver.close()


if __name__ == "__main__":
    run()
