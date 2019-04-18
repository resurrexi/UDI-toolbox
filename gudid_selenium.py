from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging


class GUDID:
    _BASE_URL = 'https://gudid.fda.gov/gudid'
    _DRIVER = webdriver.Chrome()

    def __init__(self, user, pw):
        self.user = user
        self.pw = pw
        self._DRIVER.implicitly_wait(10)

    @staticmethod
    def sleep(t):
        time.sleep(t)
        return True

    def _test_overlay_invisibility(self):
        time.sleep(1)

        wait = WebDriverWait(self._DRIVER, 30)
        # wait.until(EC.visibility_of_element_located(
        #     (By.CSS_SELECTOR, 'iframe.ice-blockui-overlay')
        # ))
        wait.until(EC.invisibility_of_element(
            (By.CSS_SELECTOR, 'iframe.ice-blockui-overlay')
        ))
        return True

    def _validate_manage_draft_page(self):
        wait = WebDriverWait(self._DRIVER, 5)

        success = False
        while success is False:
            try:
                try:
                    cell = wait.until(EC.presence_of_element_located(
                        (By.NAME, 'diForm:diResultTbl:__5w')
                    ))
                except TimeoutException:
                    cell = wait.until(EC.presence_of_element_located(
                        (By.NAME, 'diForm:diResultTbl:__6d')
                    ))
                assert 'DI Number' == cell.text
                success = True
            except Exception:
                self.sleep(1)
        return True

    def load_base_url(self):
        """Load base url of site.

        If the base url takes to browser to login page, then return False.
        Otherwise, return True.
        """
        logging.info("Loading base URL...")

        self._DRIVER.get(self._BASE_URL)
        if 'Login' in self._DRIVER.title:
            return False
        else:
            return True

    def login(self):
        logging.info("Logging in...")

        userfield = self._DRIVER.find_element_by_name('j_username')
        pwfield = self._DRIVER.find_element_by_name('j_password')

        userfield.send_keys(self.user)
        pwfield.send_keys(self.pw)
        pwfield.send_keys(Keys.RETURN)
        assert 'Welcome' in self._DRIVER.title
        return True

    def load_home(self):
        logging.info("Loading home page...")

        self._DRIVER.find_element_by_id('menuForm:mainMenuBar:home:link') \
            .click()
        header = self._DRIVER.find_element_by_css_selector(
            'div#__34>h2'
        )
        assert 'Welcome' in header.text

    def load_draft_page(self):
        logging.info("Loading Draft DI page...")

        self._DRIVER.find_element_by_name('homeForm:manageDraftLnk').click()
        assert 'Welcome' in self._DRIVER.title
        header = self._DRIVER.find_element_by_css_selector('form>div>h2')
        assert 'Manage Drafts' == header.text
        return True

    def load_manage_page(self):
        logging.info("Loading Manage DI page...")

        self._DRIVER.find_element_by_name('homeForm:manageDiLnk').click()
        assert 'Welcome' in self._DRIVER.title
        header = self._DRIVER.find_element_by_css_selector('form>div>h2')
        assert 'Manage Device' == header.text
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

    def fill_new_device_form(self, data, pub_date):
        # init webdriver wait instance
        wait = WebDriverWait(self._DRIVER, 30)

        # issuing agency
        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_issuingagency')
                ))).select_by_visible_text('GS1')
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # primary DI number
        success = False
        while success is False:
            try:
                primary_di = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_primDi')
                ))
                primary_di.clear()
                primary_di.send_keys(str(data['Unit UDI']))
                primary_di.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_primDi")
                val = primary_di.get_attribute('value')
                if str(val) == str(data['Unit UDI']):
                    success = True
            except Exception:
                self.sleep(1)

        # check if DI number already exists
        try:
            primary_di_check = self._DRIVER.find_element_by_css_selector(
                'span.msg_field_level'
            )
            if 'is already in use' in primary_di_check.text:
                logging.warning('{} already exists...'.format(data['Unit UDI']))

                self._DRIVER.find_element_by_name('diForm:topCancelBtn') \
                    .click()
                alert = self._DRIVER.switch_to.alert
                alert.accept()
                self._validate_manage_draft_page()
                return False
        except NoSuchElementException:
            pass

        # device count
        success = False
        while success is False:
            try:
                device_ct = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_deviceCount')
                ))
                device_ct.clear()
                device_ct.send_keys('1')
                device_ct.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_deviceCount")
                val = device_ct.get_attribute('value')
                if str(val) == '1':
                    success = True
            except Exception:
                self.sleep(1)

        # data entry labeler
        success = False
        while success is False:
            try:
                Select(wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_dunsNum')
                ))).select_by_index(1)
                self._DRIVER.find_element_by_name('diForm:in_dunsNum') \
                    .send_keys(Keys.TAB)
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # brand name
        success = False
        while success is False:
            try:
                brand = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_brandName')
                ))
                brand.clear()
                brand.send_keys('Sunbiotec')
                brand.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_brandName")
                val = brand.get_attribute('value')
                if val == 'Sunbiotec':
                    success = True
            except Exception:
                self.sleep(1)

        # model/version number
        success = False
        while success is False:
            try:
                model = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_modelVersionNum')
                ))
                model.clear()
                model.send_keys(str(data['Catalog No']))
                model.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_modelVersionNum")
                val = model.get_attribute('value')
                if val == str(data['Catalog No']):
                    success = True
            except Exception:
                self.sleep(1)

        # publish date
        success = False
        while success is False:
            try:
                publish_dt = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_effectiveDate')
                ))
                publish_dt.clear()
                publish_dt.send_keys(pub_date)
                publish_dt.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_effectiveDate")
                val = publish_dt.get_attribute('value')
                if str(val) == pub_date:
                    success = True
            except Exception:
                self.sleep(1)

        # add package DI
        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:addPackageLnk')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                package_di = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_packageDINum')
                ))
                package_di.clear()
                package_di.send_keys(str(data['Shelf UDI']))
                package_di.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_packageDINum")
                val = package_di.get_attribute('value')
                if str(val) == str(data['Shelf UDI']):
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                pkg_qty = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_packageQuantity')
                ))
                pkg_qty.clear()
                pkg_qty.send_keys('10')
                pkg_qty.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_packageQuantity")
                val = pkg_qty.get_attribute('value')
                if str(val) == '10':
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                Select(wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_containsDIPackage')
                ))).select_by_index(1)
                pkg_di = self._DRIVER.find_element_by_name(
                    'diForm:in_containsDIPackage'
                )
                pkg_di.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_containsDIPackage")
                val = pkg_di.get_attribute('value')
                if str(val) == str(data['Unit UDI']):
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:__dc')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # exempt from FDA premarket submission
        success = False
        while success is False:
            try:
                fda_checkbox = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_proExemptPremarAuth')
                ))
                fda_checkbox.click()
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_proExemptPremarAuth")
                if fda_checkbox.is_selected():
                    success = True
            except Exception:
                self.sleep(1)

        # add FDA product code
        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:addProductCodeLnk')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                fda_code = wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_FDAproductCode')
                ))
                fda_code.clear()
                fda_code.send_keys('MQH')
                fda_code.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_FDAproductCode")
                val = fda_code.get_attribute('value')
                if val == 'MQH':
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:__is')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # add FDA listing
        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:addFdaListingLnk')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                fda_listing = wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_fdaListingNum')
                ))
                fda_listing.clear()
                fda_listing.send_keys(str(data['FDA Listing']))
                fda_listing.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_fdaListingNum")
                val = fda_listing.get_attribute('value')
                if str(val) == str(data['FDA Listing']):
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:__k1')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # add GMDN
        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:addGmdnLnk')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                gmdn = wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_GMDNCode')
                ))
                gmdn.clear()
                gmdn.send_keys('38522')
                gmdn.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_GMDNCode")
                val = gmdn.get_attribute('value')
                if str(val) == '38522':
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:__lh')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # select single-use
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_deviceForSingleUse')
        ))).select_by_visible_text('Yes')

        # select lot/batch number
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_controlledbyLotNum')
        ))).select_by_visible_text('Yes')

        # select serial number
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_controlledBySerialNum')
        ))).select_by_visible_text('No')

        # select expiration date
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_controlledExpDate')
        ))).select_by_visible_text('Yes')

        # select manufacturing date
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_controlledManufacturyDate')
        ))).select_by_visible_text('Yes')

        # select donation id
        Select(wait.until(EC.presence_of_element_located(
            (By.NAME, 'diForm:in_donationIdNum')
        ))).select_by_visible_text('No')

        # select latex
        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_deviceContainLatex')
                ))).select_by_visible_text('No')
                latex = self._DRIVER.find_element_by_name(
                    'diForm:in_deviceContainLatex'
                )
                latex.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_deviceContainLatex")
                val = latex.get_attribute('value')
                if val == 'N':
                    success = True
            except Exception:
                self.sleep(1)

        # check prescription
        success = False
        while success is False:
            try:
                rx_checkbox = wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:in_RxPrescriptionStatus')
                ))
                rx_checkbox.click()
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_RxPrescriptionStatus")
                if rx_checkbox.is_selected():
                    success = True
            except Exception:
                self.sleep(1)

        # select MRI safety
        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_MRISafety')
                ))).select_by_visible_text(
                    'Labeling does not contain MRI Safety Information'
                )
                mri = self._DRIVER.find_element_by_name(
                    'diForm:in_MRISafety'
                )
                mri.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_MRISafety")
                val = mri.get_attribute('value')
                if val == 'MRI005':
                    success = True
            except Exception:
                self.sleep(1)

        # add storage and handling
        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:addDeviceStorageLnk')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_storageType')
                ))).select_by_visible_text(
                    'Special Storage Condition, Specify'
                )
                store_drop = self._DRIVER.find_element_by_name(
                    'diForm:in_storageType'
                )
                store_drop.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_storageType")
                val = store_drop.get_attribute('value')
                if val == 'OTHER':
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                store_fill = wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_specialStorageCondition')
                ))
                store_fill.clear()
                store_fill.send_keys(
                    'Keep dry, Keep away from sunlight, Store at room temperature'
                )
                store_fill.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_specialStorageCondition")
                val = store_fill.get_attribute('value')
                if val == 'Keep dry, Keep away from sunlight, Store at room temperature':
                    success = True
            except Exception:
                self.sleep(1)

        success = False
        while success is False:
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.NAME, 'diForm:__tp')
                )).click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)

        # select pack sterile
        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_devicePackSterile')
                ))).select_by_visible_text('Yes')
                sterile = self._DRIVER.find_element_by_name(
                    'diForm:in_devicePackSterile'
                )
                sterile.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_devicePackSterile")
                val = sterile.get_attribute('value')
                if val == 'Y':
                    success = True
            except Exception:
                self.sleep(1)

        # select sterilization prior
        success = False
        while success is False:
            try:
                Select(wait.until(EC.presence_of_element_located(
                    (By.NAME, 'diForm:in_reqSterilizationPriorToUse')
                ))).select_by_visible_text('No')
                sterile_prior = self._DRIVER.find_element_by_name(
                    'diForm:in_reqSterilizationPriorToUse'
                )
                sterile_prior.send_keys(Keys.TAB)
                self.sleep(1)
                # validate
                logging.info("Validating diForm:in_reqSterilizationPriorToUse")
                val = sterile_prior.get_attribute('value')
                if val == 'N':
                    success = True
            except Exception:
                self.sleep(1)
        return True

    def save_new_device_draft(self):
        success = False
        while success is False:
            try:
                self._DRIVER.find_element_by_name('diForm:bottomSaveDraftBtn') \
                    .click()
                self.sleep(1)
                success = True
            except Exception:
                self.sleep(1)
        self._validate_manage_draft_page()
        return True
