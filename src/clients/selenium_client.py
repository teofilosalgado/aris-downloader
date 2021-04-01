from __future__ import annotations

import time
import urllib.parse
from typing import Callable, List, TypedDict, Union

from models import Edge, Node
from repositories import db
from retrying import retry
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Item(TypedDict):
    url: str
    title: str


class SeleniumClient:
    # SUFFIX_TOKEN = "~ERBbIm92ZXJ2aWV3V2l0aG91dFRvb2xiYXJXb3JrZmxvdyJd"
    SUFFIX_TOKEN = ""

    def __init__(
        self, base_url: str, database_name: str, username: str, password: str
    ) -> None:
        # Initialize properties
        self.base_url: str = base_url
        self.database_name: str = database_name

        self.home_url = f"{self.base_url}/#default/home"
        self.insights_url = f"{self.base_url}/#insights/item"

        self.username = username
        self.password = password

        # Initialize database connection
        db.connect()
        db.create_tables([Node, Edge])

        # Initialize driver options and create a brand new temp profile
        options: Options = Options()
        options.headless = False
        profile: FirefoxProfile = FirefoxProfile()
        profile.set_preference("security.default_personal_cert", "Select Automatically")
        self.driver: WebDriver = webdriver.Firefox(
            firefox_profile=profile, options=options
        )
        self.action: ActionChains = ActionChains(self.driver)

        # Sign in to ARIS
        self.__sign_in()

    def __enter__(self) -> SeleniumClient:
        return self

    def __get_element_by_xpath(
        self, xpath: str, timeout: int = 30
    ) -> FirefoxWebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def __get_elements_by_xpath(
        self, xpath: str, timeout: int = 30
    ) -> List[FirefoxWebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_all_elements_located((By.XPATH, xpath))
            )
        except:
            return []

    def __get_clickable_element_by_xpath(self, xpath: str, timeout: int = 30):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def __navigate(self, url: str, title: str) -> None:
        if url not in urllib.parse.unquote(self.driver.current_url):
            self.driver.get(f"{self.insights_url}/{url}/{self.SUFFIX_TOKEN}")
            self.__get_element_by_xpath(f"//h1[contains(text(), '{title}')]")

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def __download_leaf(self, url: str) -> None:
        # Open export as PDF modal
        xpath_print_button: str = "//a[@aria-label='Imprimir o gráfico como PDF']"
        print_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            xpath_print_button
        )
        # self.action.move_to_element(print_button).perform()
        time.sleep(5)
        print_button.click()

        # Accept default formatting options
        xpath_ok_button: str = "//a[@id='gwt-debug-DynDialogOKBtnId']"
        ok_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            xpath_ok_button
        )
        # self.action.move_to_element(ok_button).perform()
        time.sleep(5)
        ok_button.click()

        # Download file
        xpath_download_button: str = "//a[@aria-label='Baixar resultado']"
        download_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            xpath_download_button
        )
        # self.action.move_to_element(ok_button).perform()
        time.sleep(5)
        download_button.click()

    def __clear_notifications(self) -> None:
        # Clear the download notification icon
        xpath_notification_button: str = "//div[@class='notifcationButton']"
        notification_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            xpath_notification_button
        )
        notification_button.click()

        xpath_clear_button: str = "//div[@class='reportsInfo-dismiss']"
        clear_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            xpath_clear_button
        )
        clear_button.click()

    def __sign_in(self) -> None:
        self.driver.get(self.home_url)
        username_input: FirefoxWebElement = self.driver.find_element_by_xpath(
            "//input[@name='username']"
        )
        password_input: FirefoxWebElement = self.driver.find_element_by_xpath(
            "//input[@name='password']"
        )
        submit_button: FirefoxWebElement = self.driver.find_element_by_xpath(
            "//button[@name='Submit']"
        )
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        submit_button.click()

        # Wait for home page to be loaded
        self.__get_element_by_xpath("//h1[@class='pageTitle']")

    def __sign_out(self) -> None:
        user_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            "//div[@class='cpn-userAction-currentUserName']"
        )
        self.action.move_to_element(user_button).perform()
        user_button.click()

        sign_out_button: FirefoxWebElement = self.__get_clickable_element_by_xpath(
            "//li[@class='cpn-userAction-navItemSignOut']"
        )
        self.action.move_to_element(sign_out_button).perform()
        sign_out_button.click()

    def __create_node(
        self, url: str, title: str, is_model: bool, parent: Node = None
    ) -> Node:
        if parent:
            node = Node.create(
                url=url,
                title=title,
                is_model=is_model,
                database_name=self.database_name,
                is_png_downloaded=False,
                is_pdf_downloaded=False,
            )
            Edge.create(source=parent, destination=node)
            return node
        else:
            return Node.create(
                url=url,
                title=title,
                is_model=is_model,
                database_name=self.database_name,
                is_png_downloaded=False,
                is_pdf_downloaded=False,
            )

    def __get_node_by_url(self, url: str) -> Union[Node, None]:
        return next(iter(Node.select().where(Node.url == url)), None)

    def traverse(self, url: str, title: str) -> None:
        visited_urls: List[str] = []
        queue: List[Item] = []

        visited_urls.append(url)
        queue.append({"url": url, "title": title})
        last_node: Union[Node, None] = None

        while queue:
            # Remove item from queue and navigate to it
            current_item: Item = queue.pop(0)
            self.__navigate(current_item["url"], current_item["title"])

            # Verify if node already exists in tree
            parent: Node = self.__get_node_by_url(
                current_item["url"]
            ) or self.__create_node(url, title, False, parent=last_node)

            # Look for groups and models
            xpath_groups: str = "//div[@data-cpn-factsheet-mark='propertyContent' and descendant::h2[contains(text(),'Subgrupos')]]//a"
            group_elements: List[FirefoxWebElement] = self.__get_elements_by_xpath(
                xpath_groups, timeout=5
            )
            xpath_models: str = "//div[@data-cpn-factsheet-mark='propertyContent' and descendant::h2[contains(text(),'Modelos')]]//a"
            model_elements: List[FirefoxWebElement] = self.__get_elements_by_xpath(
                xpath_models, timeout=5
            )

            # Function to extract node properties
            get_content: Callable[[FirefoxWebElement], Item] = lambda item: {
                "url": item.get_attribute("data-cpn-factsheet-item-id"),
                "title": item.text,
            }

            # Test if any group element was found, if so, add it to the queue
            if len(group_elements) > 0:
                group_nodes: List[Item] = list(map(get_content, group_elements))
                non_visited_group_nodes: List[Item] = [
                    neighbour
                    for neighbour in group_nodes
                    if neighbour["url"] not in visited_urls
                ]
                for neighbour in non_visited_group_nodes:
                    self.__create_node(
                        neighbour["url"], neighbour["title"], False, parent=parent
                    )
                    # MyNode(neighbour["url"], neighbour["title"], False, parent=parent)
                    visited_urls.append(neighbour["url"])
                    queue.append(neighbour)

            # Test if any model element was found, if so, add it to the tree
            if len(model_elements) > 0:
                model_nodes: List[Item] = list(map(get_content, model_elements))
                for model in model_nodes:
                    self.__create_node(
                        model["url"], model["title"], True, parent=parent
                    )

            # last_node = parent

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            self.__sign_out()
        finally:
            db.close()
            self.driver.close()
