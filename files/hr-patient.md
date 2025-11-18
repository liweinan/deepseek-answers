# React Problem - Patient Medical Records

- https://www.hackerrank.com/challenges/patient-medical-records
- https://github.com/liweinan/play-react/tree/main/src/hackerrank/patient

Below is an explanation of the medical words and terms involved in the medical records you provided, covering diagnosis, vital signs, and other related terms:

### Diagnosis
1. **Pulmonary Embolism**
    - Description: A serious medical condition, usually caused by a blood clot (blood thrombus) blocking the pulmonary artery, leading to obstructed blood flow in the lungs. May cause symptoms such as chest pain, difficulty breathing, and increased heart rate.
    - Severity: Marked as 4 in records, indicating severe, may require emergency treatment such as anticoagulant drugs or surgery.
    - Related Observations: Appears multiple times in records, accompanied by high heart rate (pulse) and high breathing rate, consistent with symptoms.

2. **Pleurisy**
    - Description: Inflammation of the pleura (membrane covering the lungs), usually caused by infection, pulmonary embolism, or other lung diseases. Typical symptoms include chest pain (especially during deep breathing) and difficulty breathing.
    - Severity: Marked as 3 in records, indicating moderate severity, may require anti-inflammatory drugs or treatment of underlying causes.
    - Related Observations: Often accompanied by higher breathing rate and mild body temperature elevation.

3. **Common Cold**
    - Description: Mild upper respiratory tract infection caused by viruses, symptoms include runny nose, cough, sore throat, and mild fever.
    - Severity: Marked as 1 in records, indicating mild, usually requires no special treatment and can resolve within a few days.
    - Related Observations: Cold cases in records are usually accompanied by elevated body temperature (101-103°F).

### Vital Signs
1. **Blood Pressure Systole**
    - Description: The pressure in arteries during heart contraction, reflecting the strength of heart pumping. Normal range is usually 90-120 mmHg.
    - Record Observations: Systolic blood pressure in records ranges from 75-100 mmHg, some are low, possibly related to patient conditions (such as cardiovascular pressure caused by pulmonary embolism) or individual differences.

2. **Blood Pressure Diastole**
    - Description: The pressure in arteries during heart relaxation, reflecting the resting state of blood vessels. Normal range is usually 60-80 mmHg.
    - Record Observations: Diastolic blood pressure in records is high (121-155 mmHg), indicating possible hypertension or circulatory system pressure related to diseases like pulmonary embolism.

3. **Pulse**
    - Description: Number of heartbeats per minute, reflecting heart activity. Normal range is 60-100 beats per minute.
    - Record Observations: Pulse in records is high (91-140 beats per minute), especially in pulmonary embolism cases (125-140 beats per minute), possibly due to hypoxia or increased heart load.

4. **Breathing Rate**
    - Description: Number of breaths per minute, reflecting respiratory system function. Normal range is 12-20 breaths per minute.
    - Record Observations: Breathing rate in records is high (16-34 breaths per minute), especially in pulmonary embolism (25-34 breaths per minute) and pleurisy cases, indicating breathing difficulty or limited lung function.

5. **Body Temperature**
    - Description: Reflects body core temperature, normal range is 97-99°F (36.1-37.2°C). Fever (>100.4°F) may indicate infection or inflammation.
    - Record Observations: Body temperature in records ranges from 97.1-103.8°F, cold cases often accompany fever (101-103.8°F), pulmonary embolism and pleurisy cases show smaller temperature changes.

### Other Terms
1. **Severity**
    - Description: Used to assess the severity of diseases, using a scale of 1 to 4 in records:
        - 1: Mild (such as common cold).
        - 3: Moderate (such as pleurisy).
        - 4: Severe (such as pulmonary embolism).
    - Function: Helps doctors determine the urgency and priority of treatment.

2. **Meta: Height**
    - Description: Patient's height, measured in centimeters (cm). Range in records is 157-174 cm.
    - Function: Used to calculate Body Mass Index (BMI) or assess health status.

3. **Meta: Weight**
    - Description: Patient's weight, measured in pounds (lbs). Range in records is 102-196 lbs.
    - Function: Combined with height to assess BMI, monitoring weight changes may reflect health status or disease progression.

4. **Timestamp**
    - Description: Records the specific time of medical data (in Unix timestamp format, milliseconds).
    - Function: Used to track the timeline of illness, determine disease progression or treatment effectiveness.

5. **UserDob**
    - Description: Patient's date of birth, format is "day-month-year".
    - Function: Used to calculate patient age, assess age-related health risks.

### Summary
The medical terms involved in the records mainly focus on respiratory system diseases (pulmonary embolism, pleurisy) and mild conditions (cold), as well as monitoring of vital signs. Pulmonary embolism and pleurisy cases show higher heart rate, breathing rate, and blood pressure, reflecting more severe conditions; cold cases are mainly characterized by fever with milder symptoms. These terms and data provide important basis for doctors' diagnosis and treatment.

If you need further analysis of data trends in the records or specific patient conditions, please let me know!

---

Test Data:


```javascript
const medical_records = [
  {
    id: "1",
    data: [
      {
        id: 6,
        timestamp: 1568550058964,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 155,
          bloodPressureSystole: 90,
          pulse: 130,
          breathingRate: 29,
          bodyTemperature: 99.2,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 173,
        },
      },
      {
        id: 7,
        timestamp: 1564691138999,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 147,
          bloodPressureSystole: 100,
          pulse: 138,
          breathingRate: 25,
          bodyTemperature: 100,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 196,
        },
      },
      {
        id: 8,
        timestamp: 1562157191823,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 122,
          bloodPressureSystole: 77,
          pulse: 91,
          breathingRate: 20,
          bodyTemperature: 101.5,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 175,
        },
      },
      {
        id: 13,
        timestamp: 1551906996274,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 121,
          bloodPressureSystole: 80,
          pulse: 91,
          breathingRate: 18,
          bodyTemperature: 101.3,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 180,
        },
      },
      {
        id: 15,
        timestamp: 1551566179628,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 136,
          bloodPressureSystole: 88,
          pulse: 112,
          breathingRate: 25,
          bodyTemperature: 99.3,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 192,
        },
      },
      {
        id: 22,
        timestamp: 1563243111785,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 139,
          bloodPressureSystole: 82,
          pulse: 105,
          breathingRate: 28,
          bodyTemperature: 97.1,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 196,
        },
      },
      {
        id: 24,
        timestamp: 1563805161434,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 144,
          bloodPressureSystole: 92,
          pulse: 137,
          breathingRate: 34,
          bodyTemperature: 102.5,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 191,
        },
      },
      {
        id: 30,
        timestamp: 1549051080085,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 130,
          bloodPressureSystole: 82,
          pulse: 114,
          breathingRate: 23,
          bodyTemperature: 98.6,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 188,
        },
      },
      {
        id: 33,
        timestamp: 1552027463340,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 133,
          bloodPressureSystole: 83,
          pulse: 126,
          breathingRate: 19,
          bodyTemperature: 99.7,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 185,
        },
      },
      {
        id: 41,
        timestamp: 1546789224456,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 151,
          bloodPressureSystole: 96,
          pulse: 130,
          breathingRate: 26,
          bodyTemperature: 103,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 1,
        userName: "John Oliver",
        userDob: "02-01-1986",
        meta: {
          height: 168,
          weight: 174,
        },
      },
    ],
  },
  {
    id: "2",
    data: [
      {
        id: 1,
        timestamp: 1565637002408,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 154,
          bloodPressureSystole: 91,
          pulse: 125,
          breathingRate: 32,
          bodyTemperature: 100,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 172,
        },
      },
      {
        id: 2,
        timestamp: 1562539731129,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 139,
          bloodPressureSystole: 81,
          pulse: 104,
          breathingRate: 20,
          bodyTemperature: 99.4,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 171,
        },
      },
      {
        id: 3,
        timestamp: 1563465027370,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 125,
          bloodPressureSystole: 76,
          pulse: 113,
          breathingRate: 22,
          bodyTemperature: 100.8,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 185,
        },
      },
      {
        id: 16,
        timestamp: 1568085122164,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 136,
          bloodPressureSystole: 85,
          pulse: 117,
          breathingRate: 29,
          bodyTemperature: 99.9,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 186,
        },
      },
      {
        id: 17,
        timestamp: 1547084560364,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 129,
          bloodPressureSystole: 79,
          pulse: 102,
          breathingRate: 16,
          bodyTemperature: 103.4,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 185,
        },
      },
      {
        id: 20,
        timestamp: 1549184918171,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 145,
          bloodPressureSystole: 94,
          pulse: 125,
          breathingRate: 25,
          bodyTemperature: 102.6,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 181,
        },
      },
      {
        id: 26,
        timestamp: 1564765981840,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 144,
          bloodPressureSystole: 90,
          pulse: 135,
          breathingRate: 28,
          bodyTemperature: 99.2,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 178,
        },
      },
      {
        id: 31,
        timestamp: 1555004832077,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 154,
          bloodPressureSystole: 90,
          pulse: 138,
          breathingRate: 26,
          bodyTemperature: 102.9,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 178,
        },
      },
      {
        id: 32,
        timestamp: 1554074088481,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 135,
          bloodPressureSystole: 82,
          pulse: 119,
          breathingRate: 29,
          bodyTemperature: 97.8,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 183,
        },
      },
      {
        id: 35,
        timestamp: 1560628606015,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 151,
          bloodPressureSystole: 98,
          pulse: 140,
          breathingRate: 27,
          bodyTemperature: 100.7,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 2,
        userName: "Bob Martin",
        userDob: "14-09-1989",
        meta: {
          height: 174,
          weight: 186,
        },
      },
    ],
  },
  {
    id: "3",
    data: [
      {
        id: 9,
        timestamp: 1548036340751,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 147,
          bloodPressureSystole: 96,
          pulse: 130,
          breathingRate: 28,
          bodyTemperature: 101,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 106,
        },
      },
      {
        id: 10,
        timestamp: 1562161672195,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 127,
          bloodPressureSystole: 78,
          pulse: 130,
          breathingRate: 22,
          bodyTemperature: 103.8,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 110,
        },
      },
      {
        id: 11,
        timestamp: 1563846626267,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 126,
          bloodPressureSystole: 75,
          pulse: 99,
          breathingRate: 22,
          bodyTemperature: 101.9,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 108,
        },
      },
      {
        id: 18,
        timestamp: 1560177927736,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 141,
          bloodPressureSystole: 96,
          pulse: 123,
          breathingRate: 29,
          bodyTemperature: 99,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 103,
        },
      },
      {
        id: 25,
        timestamp: 1551539005307,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 154,
          bloodPressureSystole: 90,
          pulse: 131,
          breathingRate: 22,
          bodyTemperature: 103,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 107,
        },
      },
      {
        id: 27,
        timestamp: 1556836728887,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 133,
          bloodPressureSystole: 84,
          pulse: 124,
          breathingRate: 26,
          bodyTemperature: 99.2,
        },
        doctor: {
          id: 2,
          name: "Dr Arnold Bullock",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 109,
        },
      },
      {
        id: 29,
        timestamp: 1551436887626,
        diagnosis: {
          id: 2,
          name: "Common Cold",
          severity: 1,
        },
        vitals: {
          bloodPressureDiastole: 124,
          bloodPressureSystole: 80,
          pulse: 129,
          breathingRate: 21,
          bodyTemperature: 102.3,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 107,
        },
      },
      {
        id: 34,
        timestamp: 1553964012428,
        diagnosis: {
          id: 3,
          name: "Pulmonary embolism",
          severity: 4,
        },
        vitals: {
          bloodPressureDiastole: 151,
          bloodPressureSystole: 95,
          pulse: 126,
          breathingRate: 29,
          bodyTemperature: 102.9,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 102,
        },
      },
      {
        id: 42,
        timestamp: 1551568255913,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 133,
          bloodPressureSystole: 86,
          pulse: 115,
          breathingRate: 26,
          bodyTemperature: 97.7,
        },
        doctor: {
          id: 3,
          name: "Dr Pilar Cristancho",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 110,
        },
      },
      {
        id: 47,
        timestamp: 1568317109556,
        diagnosis: {
          id: 4,
          name: "Pleurisy",
          severity: 3,
        },
        vitals: {
          bloodPressureDiastole: 139,
          bloodPressureSystole: 83,
          pulse: 124,
          breathingRate: 26,
          bodyTemperature: 99.7,
        },
        doctor: {
          id: 4,
          name: "Dr Allysa Ellis",
        },
        userId: 3,
        userName: "Helena Fernandez",
        userDob: "23-12-1987",
        meta: {
          height: 157,
          weight: 104,
        },
      },
    ],
  },
];

export default medical_records;
```