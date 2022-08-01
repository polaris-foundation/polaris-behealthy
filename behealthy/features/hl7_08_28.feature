Feature: HL7 ADT-A08 and A28 messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario Outline: Some messages result in only the update of patient information
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-<message_type> message
        Then the existing patient record is updated
        And an ACK AA message is sent back to Connector API
        Examples:
        | message_type                      |
        | A08 - Update patient information  |
        | A28 - Add person information      |
    
