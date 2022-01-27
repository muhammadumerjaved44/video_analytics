from behave import given, when, then, step
from decouple import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decouple import config
import yaml
from scraper import load_browser, get_profile, desktop_image_scrapper, download_image_from_fbid


@given('check the selenium hub url')
def test_implt(context):
    with open("docker-compose.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        host_name = data_loaded['services']['selenium_hub']['container_name']
    assert host_name == config('SE_EVENT_BUS_HOST')

@given('check the selenium hub port')
def test_implt(context):
    assert config('SE_EVENT_BUS_PORT') == '4444'

@given('open the dockerize browser')
def test_implt(context):
    port_number = config('SE_EVENT_BUS_PORT')
    remote_url_chrome = f'http://localhost:{port_number}/wd/hub'
    context.driver = webdriver.Remote(remote_url_chrome)

@when(u'load the "{site_name}" page')
def step_impl(context, site_name):
    context.driver.get(f'https://www.{site_name}.com/')
    context.driver.save_screenshot(f'{site_name}.png')

@given(u'make sure credentials are ok')
def step_impl(context):
    assert config('FB_MAIL') == 'mushimushi765@gmail.com'
    assert config('FB_PASS') == 'Password@1'

@then(u'login into facebook')
def step_impl(context):
    email=config('FB_MAIL')
    password=config('FB_PASS')
    context.driver.find_element_by_name("email").send_keys(email)
    context.driver.find_element_by_name("pass").send_keys(password)
    context.driver.find_element_by_name("login").click()
    context.driver.save_screenshot(f'login_page.png')

@given('load the facebook profile "{profile_name}"')
def step_impl(context, profile_name):
    context.execute_steps(u'''
        Given open the dockerize browser
        And make sure credentials are ok
        When load the "facebook" page
        Then login into facebook
    ''')
    context.profile_name = profile_name
    get_profile(context.profile_name,context.driver)


@then('collect all profile images of the profile')
def step_impl(context):
    context.all_images_collection = desktop_image_scrapper(context.profile_name, context.driver)
    assert len(context.all_images_collection) > 0

@then('download all profile images')
def step_impl(context):
    download_image_from_fbid(context.all_images_collection, context.driver)

@then(u'close the dockerize browser')
def step_impl(context):
    context.driver.quit()

