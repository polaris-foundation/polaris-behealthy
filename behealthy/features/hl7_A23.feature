Feature: HL7 ADT-A23 cancel admit messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A23 message cancels a non-existent admission
        Given I have a working location
        And a SEND patient exists
        When I receive a valid ADT-A23 message
        Then the existing location is used
        And the existing patient record is updated
        And a new cancelled encounter is created

    Scenario: A23 message cancels an existing admission
        Given I have a working location
        And a SEND patient exists
        When I receive a valid ADT-A01 message
        And I receive a valid ADT-A23 message
        Then the existing location is used
        And the existing patient record is updated
        And a new cancelled encounter is created

    Scenario: A23 message then A01 message creates a new encounter
        Given I have a working location
        And a SEND patient exists
        When I receive a valid ADT-A01 message about a new encounter
        And I receive a valid ADT-A23 message
        And I receive a valid ADT-A01 message about a existing encounter
        Then the existing location is used
        And the existing patient record is updated
        And new cancelled and open encounters are created
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search

    Scenario: A cancelled encounter with attached observations creates new discharged encounter 
        Given I have a working location
        And a SEND patient exists
        When I receive a valid ADT-A01 message
        And I submit a NEWS2 Observation Set
        And I receive a valid ADT-A23 message
        Then a discharged local encounter is created
        And the observations are connected to the discharged encounter
