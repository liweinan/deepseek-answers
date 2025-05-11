# React题 - Patient Medical Records

- https://www.hackerrank.com/challenges/patient-medical-records
- https://github.com/liweinan/play-react/tree/main/src/hackerrank/patient

以下是您提供的医疗记录中涉及的医学单词及术语的解释，涵盖了诊断、生命体征和其他相关术语：

### 诊断（Diagnosis）
1. **Pulmonary Embolism（肺栓塞）**
    - 描述：一种严重的医疗状况，通常由血栓（血液凝块）阻塞肺动脉引起，导致肺部血流受阻。可能引发胸痛、呼吸困难、心率加快等症状。
    - 严重程度（Severity）：记录中标记为4，表示严重，可能需要紧急治疗，如抗凝药物或手术。
    - 相关观察：记录中多次出现，伴随高心率（pulse）和高呼吸频率（breathing rate），符合症状。

2. **Pleurisy（胸膜炎）**
    - 描述：胸膜（覆盖肺部的膜）发炎，通常由感染、肺栓塞或其他肺部疾病引起。典型症状包括胸痛（尤其在深呼吸时）和呼吸困难。
    - 严重程度（Severity）：记录中标记为3，表示中度严重，可能需要抗炎药或治疗潜在原因。
    - 相关观察：常伴随较高的呼吸频率和轻度体温升高。

3. **Common Cold（普通感冒）**
    - 描述：由病毒引起的轻度上呼吸道感染，症状包括流鼻涕、咳嗽、喉咙痛和轻度发热。
    - 严重程度（Severity）：记录中标记为1，表示轻微，通常无需特殊治疗，数天内可自愈。
    - 相关观察：记录中感冒病例通常伴随体温升高（101-103°F）。

### 生命体征（Vitals）
1. **Blood Pressure Systole（收缩压）**
    - 描述：心脏收缩时动脉内的压力，反映心脏泵血的强度。正常范围通常为90-120 mmHg。
    - 记录观察：记录中的收缩压范围为75-100 mmHg，部分偏低，可能与患者病情（如肺栓塞导致的心血管压力）或个体差异有关。

2. **Blood Pressure Diastole（舒张压）**
    - 描述：心脏舒张时动脉内的压力，反映血管的休息状态。正常范围通常为60-80 mmHg。
    - 记录观察：记录中的舒张压较高（121-155 mmHg），表明可能存在高血压或与肺栓塞等疾病相关的循环系统压力。

3. **Pulse（脉搏/心率）**
    - 描述：每分钟心跳次数，反映心脏活动。正常范围为60-100次/分钟。
    - 记录观察：记录中脉搏偏高（91-140次/分钟），尤其在肺栓塞病例中（125-140次/分钟），可能因缺氧或心脏负荷增加。

4. **Breathing Rate（呼吸频率）**
    - 描述：每分钟呼吸次数，反映呼吸系统功能。正常范围为12-20次/分钟。
    - 记录观察：记录中呼吸频率偏高（16-34次/分钟），尤其在肺栓塞（25-34次/分钟）和胸膜炎病例中，提示呼吸困难或肺功能受限。

5. **Body Temperature（体温）**
    - 描述：反映身体核心温度，正常范围为97-99°F（36.1-37.2°C）。发热（>100.4°F）可能提示感染或炎症。
    - 记录观察：记录中体温范围为97.1-103.8°F，感冒病例常伴发热（101-103.8°F），肺栓塞和胸膜炎病例体温变化较小。

### 其他术语
1. **Severity（严重程度）**
    - 描述：用于评估疾病的严重性，记录中使用1到4的等级：
        - 1：轻微（如普通感冒）。
        - 3：中度（如胸膜炎）。
        - 4：严重（如肺栓塞）。
    - 作用：帮助医生判断治疗的紧急性和优先级。

2. **Meta: Height（身高）**
    - 描述：患者的身高，单位为厘米（cm）。记录中范围为157-174 cm。
    - 作用：用于计算体质指数（BMI）或评估健康状况。

3. **Meta: Weight（体重）**
    - 描述：患者的体重，单位为磅（lbs）。记录中范围为102-196 lbs。
    - 作用：结合身高评估BMI，监测体重变化可能反映健康状态或疾病进展。

4. **Timestamp（时间戳）**
    - 描述：记录医疗数据的具体时间（以Unix时间戳格式，毫秒为单位）。
    - 作用：用于追踪病情的时间线，判断疾病的进展或治疗效果。

5. **UserDob（出生日期）**
    - 描述：患者的出生日期，格式为“日-月-年”。
    - 作用：用于计算患者年龄，评估与年龄相关的健康风险。

### 总结
记录中涉及的医学术语主要围绕呼吸系统疾病（肺栓塞、胸膜炎）和轻症（感冒），以及生命体征的监测。肺栓塞和胸膜炎病例显示较高的心率、呼吸频率和血压，反映病情较重；感冒病例则以发热为主，症状较轻。这些术语和数据为医生提供了诊断和治疗的重要依据。

如果您需要进一步分析记录中的数据趋势或特定患者的病情，请告诉我！

---

测试数据：


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