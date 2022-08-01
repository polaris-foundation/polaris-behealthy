Feature: Viewing Patient in Ward List
    As a clinician
    I want the ward list to show a correct count of patients in a ward
    So that I can see at a glance how many patients are in a ward

    Scenario: Create 5 patients located at the ward and a child location
        Given I have a ward location W1 which is a child of nobody
        And I have a bay location B1 which is a child of W1
        And a SEND patient exists
        And has an open encounter at W1
        And a SEND patient exists
        And has an open encounter at W1
        And a SEND patient exists
        And has an open encounter at W1
        And a SEND patient exists
        And has an open encounter at B1
        And I have a bed location C1 which is a child of B1
        And a SEND patient exists
        And has an open encounter at C1
        Then there are 5 patients registered against W1 in the ward list
