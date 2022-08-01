Feature: HL7 ADT-A03 discharge messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A03 message results in patient discharge
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A03 for existing encounter
        Then the existing location is used
        And the existing patient record is updated
        And the encounter is marked as discharged
        And the patient does not appear on the ward list for their location
        And the patient and discharged encounter can be found via search
        And an ACK AA message is sent back to Connector API
