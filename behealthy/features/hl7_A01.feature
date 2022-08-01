Feature: HL7 ADT-A01 admit messages
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A01 message creates new patient, location, and encounter
        When I receive a valid ADT-A01 message
        Then a new patient record is created
        And a new encounter is created
        And a new location is created
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 message creates new patient and encounter at existing location
        Given I have a working location
        When I receive a valid ADT-A01 message
        Then the existing location is used
        And a new patient record is created
        And a new encounter is created
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 message updates an existing patient and creates new encounter
        Given I have a working location
        And a SEND patient exists
        When I receive a valid ADT-A01 message
        Then the existing location is used
        And the existing patient record is updated
        And a new encounter is created
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 message updates an existing patient and local encounter
        Given I have a working location
        And a SEND patient exists
        And has an open encounter
        When I receive a valid ADT-A01 message
        Then the existing location is used
        And the existing patient record is updated
        And the existing encounter is updated
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 updates an existing patient and EPR encounter
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A01 message
        Then the existing location is used
        And the existing patient record is updated
        And the existing encounter is updated
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 message with non-latin1 characters is processed correctly
        Given I have a working location
        When I receive a valid ADT-A01 message with non-latin1 characters
        Then a new patient record is created
        And a new encounter is created
        And a new location is created
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API

    Scenario: A01 message creates a new encounter even when there are existing open encounters
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A01 message about a new encounter
        Then the existing location is used
        And a new encounter is created alongside the old one
        And an ACK AA message is sent back to Connector API

    Scenario Outline: A01 message creates a new encounter based on the location's default score system
        Given I have a working location with a default score system of <default>
        And a SEND patient exists
        When I receive a valid ADT-A01 message
        Then the existing location is used
        And the existing patient record is updated
        And a new encounter is created
        And the new encounter has a score system of <score_system>
        And the patient appears on the ward list for their location
        And the patient and admitted encounter can be found via search
        And an ACK AA message is sent back to Connector API
        Examples:
            | default | score_system |
            | news2   | news2        |
            | meows   | meows        |
            | NULL    | news2        |

    @SEND_2339
    Scenario Outline: Two encounters for single patient
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        And I receive a valid ADT-A01 message about a <encounter_1> encounter
        And I receive a valid ADT-A01 message about a <encounter_2> encounter
        When I receive a valid ADT-A03 for <encounter_3> encounter
        Then the <encounter_3> encounter is discharged
        And the <encounter_4> encounter is open
        Examples:
            | encounter_1 | encounter_2 | encounter_3 | encounter_4 |
            | first       | second      | first       | second      |
            | first       | second      | second      | first       |
