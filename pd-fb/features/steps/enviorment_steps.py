from behave import given, when, then, step
from decouple import config


@given('verify the developmet enviorment')
def isEnviormentDevelopment(context):
    assert config('POINT_DUTY_ENV') == 'development'

@given('not have testing enviorment')
def isEnviormentTesting(context):
    assert config('POINT_DUTY_ENV') != 'testing'

@given('not have production enviorment')
def isEnviormentProduction(context):
    assert config('POINT_DUTY_ENV') != 'production'

@then('verify the driver running flag from the docker is True')
def isDockerTrue(context):
    assert config('DRIVER_DOCKER') == str(True)