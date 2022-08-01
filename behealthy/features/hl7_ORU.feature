Feature: HL7 ORU observation result messages
    As a clinician
    I want observations to be sent to EPR
    So that I have patients' medical details up to date in EPR

    Scenario: NEWS2 observation set generates ORU message
        Given I have a working location
        And I am a Clinician using SEND Entry
        And a SEND patient exists
        And has an open encounter
        When I submit a NEWS2 Observation Set
        Then the observation set is marked sent in Connector API

    Scenario: MEOWS observation set generates ORU message
        Given I have a working location
        And I am a Clinician using SEND Entry
        And a SEND patient exists
        And has an open encounter
        When I submit a MEOWS Observation Set
        Then the observation set is marked sent in Connector API
