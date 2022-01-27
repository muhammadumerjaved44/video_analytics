Feature: browser testing
  Scenario: check selenium browser is running
    Given verify the developmet enviorment
    And check the selenium hub url
    And check the selenium hub port
    And open the dockerize browser
    When load the "google" page
    Then close the dockerize browser


  Scenario: check facebook is running
    Given open the dockerize browser
    When load the "facebook" page
    Then close the dockerize browser

  Scenario: check facebook login
    Given open the dockerize browser
    And make sure credentials are ok
    When load the "facebook" page
    Then login into facebook
    And close the dockerize browser

  Scenario: scrape all profile images
    Given load the facebook profile "alfred.lua"
    Then collect all profile images of the profile
    Then download all profile images
    And close the dockerize browser


