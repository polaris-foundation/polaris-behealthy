Feature: HL7 ADT-A02 transfer messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A02 message results in patient transfer
        Given I have a working location
        And I have another location to transfer to
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A02 message
        Then the existing patient record is updated
        And the encounter has the expected location history
        And the patient appears on the ward list for their new location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API
