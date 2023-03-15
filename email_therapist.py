from typing import Optional  # Literal, Optional
import time
import argparse
import re
import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import urllib
import tempfile
import os
import pydub
from speech_recognition import (
    Recognizer,
    AudioFile,
)


def is_valid_phone_number(phone_number: str) -> bool:
    # Define a regular expression for a valid phone number
    pattern = r"^\d{3}-\d{3}-\d{4}$"
    # Check if the phone number matches the pattern
    return re.match(pattern, phone_number) is not None


def is_valid_email_address(email_address: str) -> bool:
    # Define a regular expression for a valid email address
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    # Check if the email address matches the pattern
    return re.match(pattern, email_address) is not None


# pylint: disable=missing-function-docstring,missing-return-docstring
def _get_driver(chrome_driver_path: str) -> webdriver.Chrome:
    driver = webdriver.Chrome(
        chrome_driver_path,
    )  # noqa: E501
    return driver


def move_mouse_around_randomly(
    driver: webdriver.Chrome,
    actions: ActionChains,
) -> None:
    window_width = driver.execute_script("return window.innerWidth")
    window_height = driver.execute_script("return window.innerHeight")
    end_time = time.time() + 10  # 10 seconds from now
    while time.time() < end_time:
        # generate random coordinates within the window
        x = random.randint(0, window_width)
        y = random.randint(0, window_height)

        # move the mouse to the random coordinates
        actions.move_by_offset(x, y).perform()

        # add a brief pause to simulate human-like movements
        time.sleep(random.uniform(1, 2))


def email_therapists(
    chrome_driver_path: str,
    url: str,
    name: str,
    email_address: str,
    phone_number: str,
    subject: str,
    message: str,
    gender: Optional[str],  # Literal["Women", "Men", "Non-Binary", None],
    issues: Optional["list[str]"],
    num_pages: int,
) -> None:
    assert is_valid_email_address(email_address)
    assert is_valid_phone_number(phone_number)
    driver = _get_driver(chrome_driver_path)

    # Navigate to the website that contains the email buttons
    driver.get(url)
    actions = ActionChains(driver)
    # Select gender if desired.
    if gender is not None:
        gender_button = driver.find_element_by_xpath(
            "//span[contains(text(), 'Gender')]"
        )
        actions.move_to_element(gender_button)
        gender_button.click()
        time.sleep(2)
        specific_gender_button = driver.find_element_by_xpath(
            f"//a[contains(text(), 'Show Me {gender}')]"
        )
        actions.move_to_element(specific_gender_button)
        specific_gender_button.click()
        time.sleep(2)

    # select which issue specialities the therapist should have
    if issues is not None:
        for issue in issues:
            try:
                # filter button hides issues
                filter_button = driver.find_element_by_class_name("refinement-button")
                actions.move_to_element(filter_button)
                filter_button.click()
            except:
                # issues button is visible
                issues_button = driver.find_element_by_xpath(
                    "//span[contains(text(), 'Issues')]"
                )
                actions.move_to_element(issues_button)
                issues_button.click()

            more_issues_button = driver.find_element_by_xpath(
                "//a[contains(text(), 'Show More Issues')]"
            )
            actions.move_to_element(more_issues_button)
            more_issues_button.click()
            time.sleep(5)
            issue_button = driver.find_element_by_xpath(
                f"//span[contains(text(), '{issue}')]"
            )
            actions.move_to_element(issue_button)
            issue_button.click()  # will cause a redirect
            time.sleep(5)

    for page in range(num_pages):
        # navigate to the new page
        driver.get(re.sub(r"&page=.", f"&page={page}", driver.current_url))
        # Find all the email buttons on the page
        email_buttons = driver.find_elements_by_xpath(
            "//button[contains(text(), 'Email')]"
        )
        email_buttons[0].click()
        driver.refresh()
        actions = ActionChains(driver)
        email_buttons = driver.find_elements_by_xpath(
            "//button[contains(text(), 'Email')]"
        )
        actions.move_to_element(email_buttons[0])
        email_buttons[0].click()
        time.sleep(4)

        close_button = driver.find_element_by_css_selector("svg.close-btn")
        actions.move_by_offset(
            close_button.location["x"], close_button.location["y"]
        ).perform()
        actions.click().perform()
        driver.refresh()
        email_buttons = driver.find_elements_by_xpath(
            "//button[contains(text(), 'Email')]"
        )
        time.sleep(10)
        N = len(email_buttons)
        # Loop through each email button
        for i in range(N):
            # Click the email button
            email_buttons = driver.find_elements_by_xpath(
                "//button[contains(text(), 'Email')]"
            )
            email_button = email_buttons[i]
            actions.move_to_element(email_button)
            email_button.click()
            driver.execute_script(
                "document.getElementsByClassName('button primary')[0].style.display = 'block';"
            )

            time.sleep(2)

            # Populate the form fields with the required information
            name_address_field = driver.find_element_by_id("name")
            actions.move_to_element(name_address_field)
            name_address_field.click()
            name_address_field.send_keys(name)
            time.sleep(1)

            email_address_field = driver.find_element_by_id("email")
            email_address_field.send_keys(email_address)
            time.sleep(1)

            phone_number_field = driver.find_element_by_id("phone")
            phone_number_field.send_keys(phone_number)
            time.sleep(1)

            subject_field = driver.find_element_by_id("subject")
            subject_field.send_keys(subject)
            time.sleep(1)

            message_field = driver.find_element_by_id("body")
            message_field.send_keys(message)
            time.sleep(1)
            # recaptcha

            try:
                print("Please note you may need to solve the recaptcha.")
                time.sleep(5)
                # switch to the iFrame containing the reCAPTCHA widget
                # In the context of reCAPTCHA, the reCAPTCHA widget is typically embedded within an iFrame element. When you load a web page that contains a reCAPTCHA widget, the widget is loaded within the iFrame. The iFrame serves as a boundary between the parent page and the reCAPTCHA widget, preventing the parent page from directly interacting with the widget.
                # This design is intended to prevent automated programs (bots) from interacting with the reCAPTCHA widget, as the widget requires human interaction to solve the challenge. By embedding the widget within an iFrame, it is more difficult for bots to access and interact with the widget directly, as they cannot simply access the HTML elements of the widget from the parent page.
                frame = driver.find_element_by_xpath('//iframe[@title="reCAPTCHA"]')
                driver.switch_to.frame(frame)

                # maybe this? https://medium.com/geekculture/how-to-solve-google-recaptcha-v3-with-python-9f92bb0212bf
                # time.sleep(10)
                # find the reCAPTCHA checkbox element and click it
                recaptcha_checkbox = driver.find_element_by_xpath(
                    '//span[@aria-checked="false"]'
                )
                recaptcha_checkbox.click()
                time.sleep(5)
                # audio challenge
                try:
                    driver.switch_to.default_content()
                    time.sleep(2)
                    audio_frame = driver.find_elements_by_tag_name("iframe")[-1]
                    driver.switch_to.frame(audio_frame)
                    time.sleep(2)
                    driver.find_element_by_id("recaptcha-audio-button").click()
                    time.sleep(2)
                    audio_src = driver.find_element_by_id("audio-source").get_attribute(
                        "src"
                    )
                    with tempfile.NamedTemporaryFile() as tf:
                        audio_path = os.path.join(tf.name + "audio.mp3")
                        urllib.request.urlretrieve(audio_src, audio_path)

                        sound = pydub.AudioSegment.from_mp3(audio_path).export(
                            audio_path.replace(".mp3", ".wav"), format="wav"
                        )
                        recognizer = Recognizer()
                        recaptcha_audio = AudioFile(audio_path.replace(".mp3", ".wav"))
                        with recaptcha_audio as source:
                            audio = recognizer.record(source)

                        text = recognizer.recognize_google(audio)

                    audio_input = driver.find_element_by_id("audio-response")
                    audio_input.send_keys(text.lower())
                    audio_input.send_keys(Keys.ENTER)
                    time.sleep(2)
                    driver.switch_to.default_content()
                except Exception as e:
                    raise e
            except NoSuchElementException:
                print("recaptcha not found")
                driver.refresh()
                continue

            # Submit the form
            submit_button = driver.find_element_by_xpath(
                "//div[contains(text,  'Send Email')]"
            )
            actions.move_to_element(submit_button)
            submit_button.click()

            time.sleep(2)

        close_button = driver.find_element_by_css_selector("svg.close-btn")
        actions.move_by_offset(
            close_button.location["x"], close_button.location["y"]
        ).perform()
        actions.click().perform()

        # Switch back to the original page
        # driver.switch_to.window(driver.window_handles[0])

    # Close the browser window
    driver.quit()


def run() -> None:
    parser = argparse.ArgumentParser(description="Automate emailing a therapist.")
    parser.add_argument(
        "--email_address",
        required=True,
        help="Your email address where a therapist should contact you.",
    )
    parser.add_argument("--phone_number", required=True, help="Your phone number.")
    parser.add_argument("--subject", required=True, help="The email subject header.")
    parser.add_argument(
        "--message_file_path",
        required=True,
        help="A path to a .txt file that contains your message to the therapist.",
    )
    parser.add_argument(
        "--num_pages",
        required=False,
        default=3,
        help="Number of pages to scroll through.",
    )

    email_therapists(
        chrome_driver_path="./chromedriver_mac64/chromedriver",
        url="https://www.psychologytoday.com/us/therapists/ca/oakland",
        name="bubby",
        email_address="dong@gmail.com",
        phone_number="408-555-5555",
        subject="Subject",
        message="Reaching out for care",
        gender="Women",
        issues=["Trauma and PTSD"],
        num_pages=3,
    )


if __name__ == "__main__":
    run()
