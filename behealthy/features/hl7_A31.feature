Feature: HL7 ADT-A31 messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A31 message results in update of patient information
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A31 message
        Then the existing patient record is updated
        And an ACK AA message is sent back to Connector API
    
    Scenario: A31 message with missing PID segment results in no update of patient information
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive an ADT-A31 message with missing PID
        Then the existing patient record is not updated
        And an ACK AE message is sent back to Connector API

    Scenario Outline: A31 message with certain missing segment results with update of patient information
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive an ADT-A31 message with missing <segment>
        Then the existing patient record is updated
        And an ACK AA message is sent back to Connector API
        Examples:
        | segment |
        | PVN     |
        | EVN     |
