from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait


class element_is_enabled:
    """Custom wait condition to check if element is enabled."""
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if element.is_enabled():
            return element
        else:
            return False


class GUDID:
    _BASE_URL = 'https://gudid.fda.gov/gudid'
    _DRIVER = webdriver.Chrome()

    def __init__(self, user, pw, gs1='697029914'):
        self.user = user
        self.pw = pw
        self.gs1 = gs1

    def _load_base_url(self):
        """Load base url of site.

        If the base url takes to browser to login page, then return False.
        Otherwise, return True.
        """
        self._DRIVER.get(self._BASE_URL)
        if 'Login' in self._DRIVER.title:
            return False
        else:
            return True

    def _login(self):
        userfield = self._DRIVER.find_element_by_name('j_username')
        pwfield = self._DRIVER.find_element_by_name('j_password')
        userfield.send_keys(self.user)
        pwfield.send_keys(self.pw)
        pwfield.send_keys(Keys.RETURN)
        assert 'Welcome' in self._DRIVER.title
        return True

    def load_draft_page(self):
        self._DRIVER.find_element_by_name('homeForm:manageDraftLnk').click()
        assert 'Welcome' in self._DRIVER.title
        header = self._DRIVER.find_element_by_css_selector('form>div>h2')
        assert 'Manage Drafts' == header.text
        return True

    def load_new_device_page(self):
        buttons = self._DRIVER.find_elements_by_css_selector('a.btn.btn_blue')
        to_click = None
        for button in buttons:
            if button.text == 'New DI':
                to_click = button
                break
        if to_click is not None:
            to_click.click()
            return True
        else:
            return False

    def fill_new_device_form(self, data):
        agency = Select(
            self._DRIVER.find_element_by_name('diForm:in_issuingagency')
        )
        agency.select_by_visible_text('GS1')

        # wait until primDi input field is enabled
        wait = WebDriverWait(self._DRIVER, 10)
        primDi = wait.until(element_is_enabled((By.NAME, 'diForm:in_primDi')))

        # now send value to field
        primDi.send_keys()
