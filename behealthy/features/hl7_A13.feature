Feature: HL7 ADT-A13 cancel discharge messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A13 message cancels a patient discharge
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A03 for existing encounter
        And I receive a valid ADT-A13 message
        Then the existing location is used
        And the existing patient record is updated
        And the encounter is not marked as discharged
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API
