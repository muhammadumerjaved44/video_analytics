Feature: enviorment testing
  Scenario: check enviorment settings
    Given verify the developmet enviorment
    And not have testing enviorment
    And not have production enviorment
    Then verify the driver running flag from the docker is True