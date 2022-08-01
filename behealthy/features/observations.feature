Feature: Taking observations in SEND
    As a clinician
    I want the observations I take to be saved in the system
    So that I can see them later

    Scenario: Creating an observation set results in an updated PDF
        Given I have a working location
        And I am a Clinician using SEND Entry
        And I have a valid jwt
        And a SEND patient exists
        And has an open encounter
        And has no BCP PDF
        When I submit a NEWS2 Observation Set
        Then the BCP PDF is generated

    Scenario: Creating an observation set allows it to be stored
        Given I have a working location
        And I am a Clinician using SEND Entry
        And a SEND patient exists
        And has an open encounter
        And I have no existing observation sets
        When I submit a NEWS2 Observation Set
        Then I have an Observation Set with a Score
