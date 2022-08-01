Feature: HL7 ADT-A04 message scenarios
    As a clinician
    I want products to be kept in sync with EPR
    So that I have an accurate patient list

    Scenario: A new patient record and encounter are created for patient who has not been admitted yet
        Given I have a working location
        When I receive a valid ADT-A04 - Register a patient message
        Then a new patient record is created
        And a new encounter is created
        And an ACK AA message is sent back to Connector API

    Scenario: Patient record is updated for an existing patient
        Given I have a working location
        And a SEND patient exists
        And an EPR encounter exists
        When I receive a valid ADT-A04 - Register a patient message
        Then the existing patient record is updated
        And an ACK AA message is sent back to Connector API
  
