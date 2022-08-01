# SYNE scenarios have been disabled as DEV is not running SYNE
# Once SYNE is reinstated the commented features require enabling
# and the final scenario needs to be removed

@syne
Feature: Creating and verifying GDM SYNE Predictions
#     As a clinician
#     I want to be able to check SYNE predictions for my GDM patients
#     So that there is Medication advice generated when necessary

#     Scenario Outline: Verifying GDM patients with SYNE predictions
#         Given a GDM patient exists
#         And I generate certain BG readings "<bgreadingsfile>"
#         When I trigger SYNE processing
#         Then I see the expected SYNE predictions "<syneprediction>" "<medsprediction>" "<predictionvalue>" "<imputed>" "<imputedvalue>"
#         Examples: Data
#         | bgreadingsfile               | syneprediction   | medsprediction | predictionvalue| imputed | imputedvalue |
#         | syne_readings_scenario.json  | CONSIDER_MEDS    | MEDS           | 0.624          | False   | 6.0          |


#     Scenario Outline: Verifying GDM patients with NO_MEDS predictions
#         Given a GDM patient exists
#         And I generate certain BG readings "<bgreadingsfile>"
#         When I trigger SYNE processing
#         Then I see No SYNE predictions
#         Examples: Data
#         | bgreadingsfile               |
#         | syne_readings_no_meds.json   | 

#     Scenario Outline: Verify GDM patient has no SYNE predictions
#         Given a GDM patient exists
#         And I generate certain BG readings "<bgreadingsfile>"
#         When I trigger SYNE processing
#         Then I see No SYNE predictions
#         Examples: Data
#         | bgreadingsfile                    |
#         | syne_no_prediction_scenario.json  |

    Scenario Outline: Verify that SYNE is disabled on DEV
        Given a GDM patient exists
        And I generate certain BG readings "<bgreadingsfile>"
        When I attempt SYNE processing when SYNE is disabled
        Then I see No SYNE data produced
        Examples: Data
        | bgreadingsfile                    |
        | syne_no_prediction_scenario.json  |
