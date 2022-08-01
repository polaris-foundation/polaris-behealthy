Feature: Creating and retrieving GDM PDFs
    As a clinician
    I want to be able to print reports for my GDM patients
    So that I can revert to paper when necessary

    Scenario: Existing GDM PDF is retrieved
        Given a GDM patient exists
        And a GDM PDF exists for that patient
        When I request the PDF
        Then I receive the PDF
        And the PDF has not been regenerated

    Scenario: New GDM PDF is generated and retrieved
        Given a GDM patient exists
        And a GDM PDF does not exist for that patient
        When I request the PDF
        Then I receive the PDF
