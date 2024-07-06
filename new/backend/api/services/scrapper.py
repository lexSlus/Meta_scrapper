import contextlib
import logging
import os
import time
from secrets import SystemRandom
from typing import Dict

import seleniumwire.undetected_chromedriver as webdriver
from bs4 import BeautifulSoup, Tag
from django.conf import settings
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait

from api.dto import FakeAccount, GroupDTO, Lead

logger = logging.getLogger(__name__)


class WebDriverManager:
    def __init__(self, proxy_url: str):
        selenium_options = {
            "proxy": {
                "http": proxy_url,
            }
        }

        self.driver = webdriver.Chrome(
            options=self._init_options(),
            seleniumwire_options=selenium_options,
            # It fixes at least:
            # urllib.error.HTTPError: HTTP Error 404: Not Found
            # issues with asynchronimous tasks
            # from undetected_chromedriver package
            # There were a few more that weren't recorded
            version_main=112,
            driver_executable_path="/usr/lib/chromium/chromedriver",
        )

        self.driver.implicitly_wait(4)

        self.proxy = proxy_url
        # We need this ip later to check if browser is using it
        self.proxy_ip = proxy_url.split("@")[-1].split(":")[0]

    def __enter__(self) -> WebDriver:
        # Check browser IP
        # self.healthcheck()

        # Check if browser is undetectable (script should return False)
        st = self.driver.execute_script("return navigator.webdriver")
        assert not st

        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.driver.quit()

        os.waitpid(self.driver.browser_pid, 0)
        os.waitpid(self.driver.service.process.pid, 0)

    def _init_options(self) -> Options:
        options = Options()

        # Do not open browser window
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--np-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Disable warning if page is suspicious (using http)
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        # Do not load images
        options.add_argument("--blink-settings=imagesEnabled=false")
        # Don't allow notifications in pop-up message
        options.add_argument("--disable-notifications")

        return options

    def healthcheck(self) -> None:
        self.driver.get("http://jsonip.com")
        assert self.proxy_ip in self.driver.find_element(By.TAG_NAME, "body").text


class Scrapper:
    # Wait time to simulate user actions
    at_least_wait = 5
    default_time = 3

    # If login is required these are messages that detects this page
    cookie = "Decline optional cookies"
    login_msg = "You must log in to continue."

    def __init__(self) -> None:
        self.rand_generator = SystemRandom()

    def get_new_posts(self, account: FakeAccount) -> Dict[str, list[Lead]]:
        new_posts: Dict[str, list[Lead]] = {}

        with WebDriverManager(account.proxy_url) as driver:
            self.handle_authorization(account, driver)

            for group in account.groups:
                posts: list[Tag] = self.get_feed_posts(driver, group, 8)

                new_posts[group.group_link] = self.get_new_posts_from_recent([post for post in posts], group)

        return new_posts

    def get_feed_posts(self, driver: WebDriver, group: GroupDTO, at_least_posts: int) -> list[Lead]:
        self.load_group_page(driver, group)

        # If not-required login popup will appear
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        scroll_position = 1
        recent_leads: list[Lead] = []

        while True:
            # Scroll down to load more posts
            # TODO: better scroll adjustment (6 was picked to avoid post to become hidden)
            driver.execute_script(f"window.scrollTo(0, {scroll_position} * document.body.scrollHeight/6);")
            # Wait for posts to load
            self.wait(4, 1)

            # Press all 'see original'
            see_original = driver.find_elements(By.XPATH, "//div[text()='See original' and @role='button']")
            for el in see_original:
                # In case see original doesn't exist
                with contextlib.suppress(
                    StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
                ):
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(el)).click()

            # Press all avialible 'see more'
            see_more = driver.find_elements(By.XPATH, "//div[text()='See more' and @role='button']")
            for el in see_more:
                with contextlib.suppress(
                    StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
                ):
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(el)).click()

            # Note: we need to hover over post timestamp, so the link is not # but real link
            # Note: not all links with '#' are related to post
            post_links = driver.find_elements(By.XPATH, "//a[@href='#']")
            for post_link in post_links:
                with contextlib.suppress(ElementNotInteractableException, StaleElementReferenceException):
                    ActionChains(driver).move_to_element(post_link).perform()

            # Note: Selenium returns the same posts multiple times
            soup = BeautifulSoup(driver.page_source, "html.parser")

            recent_leads += [
                self.get_lead_from_feed_post(post)
                for post in soup.find("div", {"role": "feed"}).find_all("div", {"role": "article"})
                if self._is_valid_post(post)
            ]
            recent_leads = list(set([lead for lead in recent_leads if lead.user_link and lead.post_link]))

            if len(recent_leads) >= at_least_posts:
                return recent_leads
            else:
                scroll_position += 1

    def wait(self, at_least_wait: int = 5, default_time: int = 3) -> None:
        """Imitates user behavior."""
        time.sleep(at_least_wait + default_time * self.rand_generator.random())

    def get_lead_from_feed_post(self, feed_post: Tag) -> Lead:
        user_link: str | None = None
        post_text: str | None = None
        post_link: str | None = None

        post_info = self._get_post_info(feed_post)

        if not post_info:
            return Lead(post_text=post_text, user_link=user_link, post_link=post_link)

        # Container with post title (user and timestamp)
        user_info = self._get_user_info(post_info)

        user_link = self._get_user_link(user_info)
        post_link = self._get_post_link(user_info)
        post_text = self._get_post_text(post_info)

        return Lead(post_text=post_text, user_link=user_link, post_link=post_link)

    def handle_authorization(self, user: FakeAccount, driver: WebDriver) -> None:
        """Set cookie or log in. Log in creates user.new_cookie."""
        driver.get(settings.FB_MAIN_LINK)

        if user.cookies:
            self.add_cookie(user.cookies, driver)

        self.wait()

        if new_cookies := self.handle_login(user, driver):
            logger.warning(f"Cookies were updated for {user.username}")
            user.new_cookies = new_cookies

            self.add_cookie(user.new_cookies, driver)

    def add_cookie(self, cookies: list[dict], driver: WebDriver) -> None:
        for cookie in cookies:
            # Supported sameSite are ["Strict", "Lax", "None"]
            # But FB cookies have 'unspecified', 'no_restriction' and 'lax'
            # TODO: research if original and supported sameSite keywords mapped correctly
            if cookie["sameSite"] in ["unspecified", "no_restriction"]:
                cookie["sameSite"] = "Lax"

            if cookie["sameSite"] == "lax":
                cookie["sameSite"] = "Lax"

            driver.add_cookie(cookie)

    def handle_login(self, user: FakeAccount, driver: WebDriver) -> list[dict] | None:
        """Returns new cookies if login page appeared, None otherwise."""
        # If cookie pop-up appears, press to decline
        with contextlib.suppress(NoSuchElementException):
            driver.find_element(By.XPATH, f"//button[@title='{self.cookie}']").click()

        # Detect if login page
        with contextlib.suppress(NoSuchElementException):
            driver.find_element(By.XPATH, f"//div[text()='{self.login_msg}']")

            # Enter credentials
            driver.find_element(By.ID, "email").send_keys(user.username)
            self.wait()
            driver.find_element(By.ID, "pass").send_keys(user.password)
            self.wait()

            driver.find_element(By.ID, "loginbutton").click()
            self.wait()

            return driver.get_cookies()

    def load_group_page(self, driver: WebDriver, group: GroupDTO) -> None:
        # Go to the group page and wait untill loaded
        # Reload if doesn't want to load
        while True:
            driver.get(group.group_link)
            self.wait()

            # Check if not group page appeared
            assert driver.current_url == group.group_link

            if driver.find_element(By.XPATH, "//div[@role='feed']"):
                break

    def get_new_posts_from_recent(self, recent: list[Lead], group: GroupDTO) -> list[Lead]:
        # Timestamp is not reliable for detecting new posts
        # Example: if a few posts have '1m'
        last_lead_index = [
            index for index, post in enumerate(recent) if post.post_link and post.post_link == group.last_post_link
        ]

        # If last lead is in the gathered posts -- trim the posts till it
        # Include all posts otherwise
        return recent[: last_lead_index[0]] if last_lead_index else recent

    def _get_post_info(self, feed_post: Tag) -> list[Tag] | None:
        """Returns an array of Tags containing user's information in a post.

        Args:
            feed_post (Tag): The Beautiful Soup Tag object representing a post.

        Returns:
            Union[List[Tag], None]: An array of Tags containing user information if found in the post.
                                    Returns None if post info in feed_post wasn't found,
                                    which is common if the post is hidden.

        Notes:
            This function traverses the given feed_post to extract user information
            from the post. It looks for specific HTML structure and attributes to identify
            user profile data and post text within the post. These Tags contains an empty div,
            user information AKA header, data about post.
        """
        while True:
            # Go until find a div with style inner attr
            try:
                # Container with post data has inline style attribute
                # 'broken' post has style=""
                if not feed_post["style"]:
                    feed_post = feed_post.contents[0]
                    continue
                if "aria-hidden" in feed_post.attrs:
                    break
                # Container with user profile data (with a timestamp) and post text
                for div in feed_post.contents[0].contents:
                    if "class" not in div.attrs and div.contents:
                        return div.contents[0].contents[0].contents[1:]

            except KeyError:
                # Go to the child element
                # Exit in case of no data in the div
                try:
                    feed_post = feed_post.contents[0]
                except IndexError:
                    break

    def _get_user_info(self, post_info: list[Tag]) -> Tag:
        return post_info[0].contents[0].contents[1]

    def _get_post_link(self, user_info: Tag) -> str:
        post_link = user_info.contents[0].contents[1].find("a")["href"]
        return post_link[: post_link.find("?__cft__[0]")]

    def _get_user_link(self, user_info: Tag) -> str:
        user_link = user_info.find("a")["href"]
        return user_link[: user_link.find("?__cft__[0]")]

    def _get_post_text(self, post_info: list[Tag]) -> str:
        post_text = ""
        for el in post_info[1].contents:
            # If a simple message
            if "data-ad-comet-preview" in el.contents[0].attrs:
                post_text += el.contents[0].contents[0].text + "\n"
            # If original text
            elif el.name == "blockquote":
                post_text += "Translated text: " + el.contents[0].contents[0].text
            # If inner message
            elif len(el.contents[0].contents[0].contents) == 3:
                # If a picture (<a href="photo"/>)
                if el.contents[0].contents[0].name == "a":
                    continue
                # If inserted something
                else:
                    try:
                        post_text += el.contents[0].contents[0].contents[-1].contents[0].text + "\n"
                    except IndexError:
                        post_text += "Inserted message doesn't contain any text\n"
            # If forwarded message
            elif len(el.contents[0].contents) == 3:
                if el.find("div", {"data-ad-comet-preview": "message"}):
                    post_text += el.find("div", {"data-ad-comet-preview": "message"}).text
                else:
                    logger.warning(f"Undetected text in post: {self._get_post_link(self._get_user_info(post_info))}")
            # If inserted images
            elif set(("class", "id")) == set(el.attrs.keys()):
                continue

            else:
                post_text += el.text + "\n"

        return post_text if post_text else "No text available"

    def _is_valid_post(self, post: Tag) -> bool:
        return (
            "class" in post.attrs
            and post.contents
            and "hidden" not in post.contents[0].contents[0].attrs
            and "aria-posinset" in post.attrs
        )
