
## [Creating and retrieving GDM PDFs](toc/behealthy/features/gdm_pdf.feature#L1)


As a clinician
I want to be able to print reports for my GDM patients
So that I can revert to paper when necessary

### Scenarios


#### [Existing GDM PDF is retrieved](toc/behealthy/features/gdm_pdf.feature#L6)



#### [New GDM PDF is generated and retrieved](toc/behealthy/features/gdm_pdf.feature#L13)



---

## [Creating and verifying GDM SYNE Predictions](toc/behealthy/features/gdm_syne.feature#L6)



### Scenarios


#### [Verify that SYNE is disabled on DEV](toc/behealthy/features/gdm_syne.feature#L39)



---

## [HL7 ADT-A08 and A28 messages](toc/behealthy/features/hl7_08_28.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [Some messages result in only the update of patient information](toc/behealthy/features/hl7_08_28.feature#L6)



---

## [HL7 ADT-A01 admit messages](toc/behealthy/features/hl7_A01.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A01 message creates new patient, location, and encounter](toc/behealthy/features/hl7_A01.feature#L6)



#### [A01 message creates new patient and encounter at existing location](toc/behealthy/features/hl7_A01.feature#L15)



#### [A01 message updates an existing patient and creates new encounter](toc/behealthy/features/hl7_A01.feature#L25)



#### [A01 message updates an existing patient and local encounter](toc/behealthy/features/hl7_A01.feature#L36)



#### [A01 updates an existing patient and EPR encounter](toc/behealthy/features/hl7_A01.feature#L48)



#### [A01 message with non-latin1 characters is processed correctly](toc/behealthy/features/hl7_A01.feature#L60)



#### [A01 message creates a new encounter even when there are existing open encounters](toc/behealthy/features/hl7_A01.feature#L70)



#### [A01 message creates a new encounter based on the location's default score system](toc/behealthy/features/hl7_A01.feature#L79)



#### [Two encounters for single patient](toc/behealthy/features/hl7_A01.feature#L97)



---

## [HL7 ADT-A02 transfer messages](toc/behealthy/features/hl7_A02.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A02 message results in patient transfer](toc/behealthy/features/hl7_A02.feature#L6)



---

## [HL7 ADT-A03 discharge messages](toc/behealthy/features/hl7_A03.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A03 message results in patient discharge](toc/behealthy/features/hl7_A03.feature#L6)



---

## [HL7 ADT-A04 message scenarios](toc/behealthy/features/hl7_A04.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A new patient record and encounter are created for patient who has not been admitted yet](toc/behealthy/features/hl7_A04.feature#L6)



#### [Patient record is updated for an existing patient](toc/behealthy/features/hl7_A04.feature#L13)



---

## [HL7 ADT-A13 cancel discharge messages](toc/behealthy/features/hl7_A13.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A13 message cancels a patient discharge](toc/behealthy/features/hl7_A13.feature#L6)



---

## [HL7 ADT-A23 cancel admit messages](toc/behealthy/features/hl7_A23.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A23 message cancels a non-existent admission](toc/behealthy/features/hl7_A23.feature#L6)



#### [A23 message cancels an existing admission](toc/behealthy/features/hl7_A23.feature#L14)



#### [A23 message then A01 message creates a new encounter](toc/behealthy/features/hl7_A23.feature#L23)



#### [A cancelled encounter with attached observations creates new discharged encounter](toc/behealthy/features/hl7_A23.feature#L35)



---

## [HL7 ADT-A31 messages](toc/behealthy/features/hl7_A31.feature#L1)


As a clinician
I want products to be kept in sync with EPR
So that I have an accurate patient list

### Scenarios


#### [A31 message results in update of patient information](toc/behealthy/features/hl7_A31.feature#L6)



#### [A31 message with missing PID segment results in no update of patient information](toc/behealthy/features/hl7_A31.feature#L14)



#### [A31 message with certain missing segment results with update of patient information](toc/behealthy/features/hl7_A31.feature#L22)



---

## [HL7 ORU observation result messages](toc/behealthy/features/hl7_ORU.feature#L1)


As a clinician
I want observations to be sent to EPR
So that I have patients' medical details up to date in EPR

### Scenarios


#### [NEWS2 observation set generates ORU message](toc/behealthy/features/hl7_ORU.feature#L6)



#### [MEOWS observation set generates ORU message](toc/behealthy/features/hl7_ORU.feature#L14)



---

## [Taking observations in SEND](toc/behealthy/features/observations.feature#L1)


As a clinician
I want the observations I take to be saved in the system
So that I can see them later

### Scenarios


#### [Creating an observation set results in an updated PDF](toc/behealthy/features/observations.feature#L6)



#### [Creating an observation set allows it to be stored](toc/behealthy/features/observations.feature#L16)



---

## [Viewing Patient in Ward List](toc/behealthy/features/send_ward_list.feature#L1)


As a clinician
I want the ward list to show a correct count of patients in a ward
So that I can see at a glance how many patients are in a ward

### Scenarios


#### [Create 5 patients located at the ward and a child location](toc/behealthy/features/send_ward_list.feature#L6)



---

## [Sending SMS messages](toc/behealthy/features/sms.feature#L2)


As a clinician
I want to be able to send SMS messages to my patients
So that I can get in touch with them

### Scenarios


#### [Sending a message in Polaris causes an SMS message to be sent using Twilio](toc/behealthy/features/sms.feature#L8)



---
