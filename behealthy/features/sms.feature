@sms
Feature: Sending SMS messages
    As a clinician
    I want to be able to send SMS messages to my patients
    So that I can get in touch with them

    @sms
    Scenario: Sending a message in Polaris causes an SMS message to be sent using Twilio
        Given a GDM patient exists
        And the patient has SMS enabled
        When I send the patient a message
        Then Polaris attempts to send an SMS message using Twilio
        Then I see that the Twilio callback has succeeded
