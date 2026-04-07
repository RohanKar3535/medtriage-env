"""
Synthetic patient case library for MedTriage-Env.
50 clinically realistic cases spanning ESI levels 1-5.
Each case includes chief complaint, gold-standard ESI, vitals, demographics,
comorbidities, deterioration rates, and required clinical actions.
"""

CASE_LIBRARY = [
    # ══════════════════════════════════════════════════════════════
    # ESI-1: RESUSCITATION — Immediately life-threatening (10 cases)
    # ══════════════════════════════════════════════════════════════
    {
        "id": "esi1_cardiac_arrest",
        "chief_complaint": "Found unresponsive on the floor, no pulse detected by bystander, CPR in progress by EMS",
        "gold_esi": 1,
        "vitals": {"heart_rate": 0, "bp_systolic": 0, "bp_diastolic": 0, "spo2": 65, "temperature": 97.2, "respiratory_rate": 0},
        "age": 62, "comorbidities": ["coronary_artery_disease", "hypertension", "diabetes"],
        "deterioration_threshold": 5,
        "required_tests": ["ECG", "troponin", "CBC", "BMP"],
        "required_consults": ["cardiology"],
    },
    {
        "id": "esi1_respiratory_failure",
        "chief_complaint": "Severe shortness of breath with cyanosis, unable to speak, accessory muscle use, tripod positioning",
        "gold_esi": 1,
        "vitals": {"heart_rate": 138, "bp_systolic": 168, "bp_diastolic": 95, "spo2": 72, "temperature": 101.8, "respiratory_rate": 42},
        "age": 71, "comorbidities": ["COPD", "heart_failure"],
        "deterioration_threshold": 5,
        "required_tests": ["CBC", "BMP", "blood_culture", "CT_chest"],
        "required_consults": ["pulmonology"],
    },
    {
        "id": "esi1_major_trauma",
        "chief_complaint": "High-speed MVC, unrestrained driver, large scalp laceration with active hemorrhage, GCS 6",
        "gold_esi": 1,
        "vitals": {"heart_rate": 132, "bp_systolic": 72, "bp_diastolic": 40, "spo2": 84, "temperature": 96.5, "respiratory_rate": 32},
        "age": 34, "comorbidities": [],
        "deterioration_threshold": 5,
        "required_tests": ["CBC", "BMP", "CT_head", "X_ray"],
        "required_consults": ["surgery", "neurology"],
    },
    {
        "id": "esi1_status_epilepticus",
        "chief_complaint": "Continuous generalized seizure lasting 15 minutes, no return to consciousness between episodes",
        "gold_esi": 1,
        "vitals": {"heart_rate": 142, "bp_systolic": 185, "bp_diastolic": 105, "spo2": 82, "temperature": 102.4, "respiratory_rate": 8},
        "age": 28, "comorbidities": ["epilepsy"],
        "deterioration_threshold": 5,
        "required_tests": ["CBC", "BMP", "CT_head"],
        "required_consults": ["neurology"],
    },
    {
        "id": "esi1_anaphylaxis",
        "chief_complaint": "Severe allergic reaction after bee sting, throat swelling, stridor, widespread urticaria, wheezing",
        "gold_esi": 1,
        "vitals": {"heart_rate": 135, "bp_systolic": 75, "bp_diastolic": 42, "spo2": 80, "temperature": 98.6, "respiratory_rate": 34},
        "age": 42, "comorbidities": ["asthma"],
        "deterioration_threshold": 5,
        "required_tests": ["CBC"],
        "required_consults": [],
    },
    {
        "id": "esi1_massive_stroke",
        "chief_complaint": "Sudden onset unresponsiveness, left-sided hemiplegia, fixed dilated right pupil, GCS 4",
        "gold_esi": 1,
        "vitals": {"heart_rate": 55, "bp_systolic": 210, "bp_diastolic": 120, "spo2": 88, "temperature": 98.2, "respiratory_rate": 10},
        "age": 68, "comorbidities": ["atrial_fibrillation", "hypertension"],
        "deterioration_threshold": 5,
        "required_tests": ["CT_head", "CBC", "BMP"],
        "required_consults": ["neurology"],
    },
    {
        "id": "esi1_tension_pneumo",
        "chief_complaint": "Sudden chest pain and dyspnea after stabbing, tracheal deviation to the left, absent breath sounds on right",
        "gold_esi": 1,
        "vitals": {"heart_rate": 140, "bp_systolic": 78, "bp_diastolic": 45, "spo2": 76, "temperature": 98.4, "respiratory_rate": 38},
        "age": 25, "comorbidities": [],
        "deterioration_threshold": 5,
        "required_tests": ["X_ray"],
        "required_consults": ["surgery"],
    },
    {
        "id": "esi1_ruptured_aaa",
        "chief_complaint": "Sudden severe abdominal and back pain, pulsatile abdominal mass, rapidly declining consciousness",
        "gold_esi": 1,
        "vitals": {"heart_rate": 128, "bp_systolic": 68, "bp_diastolic": 38, "spo2": 89, "temperature": 97.8, "respiratory_rate": 28},
        "age": 74, "comorbidities": ["hypertension", "smoking_history", "peripheral_vascular_disease"],
        "deterioration_threshold": 5,
        "required_tests": ["CBC", "BMP", "CT_chest"],
        "required_consults": ["surgery"],
    },
    {
        "id": "esi1_septic_shock",
        "chief_complaint": "High fever, rigors, confusion, mottled skin, came from nursing home with UTI symptoms",
        "gold_esi": 1,
        "vitals": {"heart_rate": 135, "bp_systolic": 70, "bp_diastolic": 35, "spo2": 86, "temperature": 104.2, "respiratory_rate": 30},
        "age": 82, "comorbidities": ["diabetes", "chronic_kidney_disease", "dementia"],
        "deterioration_threshold": 10,
        "required_tests": ["CBC", "BMP", "blood_culture", "urinalysis"],
        "required_consults": ["internal_medicine"],
    },
    {
        "id": "esi1_airway_obstruction",
        "chief_complaint": "Choking on food, unable to cough or speak, clutching throat, turning cyanotic",
        "gold_esi": 1,
        "vitals": {"heart_rate": 145, "bp_systolic": 170, "bp_diastolic": 100, "spo2": 68, "temperature": 98.6, "respiratory_rate": 4},
        "age": 55, "comorbidities": ["dysphagia"],
        "deterioration_threshold": 5,
        "required_tests": [],
        "required_consults": [],
    },

    # ══════════════════════════════════════════════════════════════
    # ESI-2: EMERGENT — High risk / severe pain (10 cases)
    # ══════════════════════════════════════════════════════════════
    {
        "id": "esi2_chest_pain_mi",
        "chief_complaint": "Crushing substernal chest pain radiating to left arm and jaw, diaphoresis, onset 30 minutes ago",
        "gold_esi": 2,
        "vitals": {"heart_rate": 108, "bp_systolic": 155, "bp_diastolic": 92, "spo2": 94, "temperature": 98.6, "respiratory_rate": 22},
        "age": 58, "comorbidities": ["hypertension", "diabetes", "smoking_history"],
        "deterioration_threshold": 20,
        "required_tests": ["ECG", "troponin", "CBC", "BMP"],
        "required_consults": ["cardiology"],
    },
    {
        "id": "esi2_stroke_symptoms",
        "chief_complaint": "Sudden right-sided facial droop, slurred speech, right arm weakness, onset 45 minutes ago",
        "gold_esi": 2,
        "vitals": {"heart_rate": 88, "bp_systolic": 178, "bp_diastolic": 98, "spo2": 96, "temperature": 98.4, "respiratory_rate": 18},
        "age": 65, "comorbidities": ["atrial_fibrillation", "hypertension"],
        "deterioration_threshold": 15,
        "required_tests": ["CT_head", "CBC", "BMP"],
        "required_consults": ["neurology"],
    },
    {
        "id": "esi2_allergic_reaction",
        "chief_complaint": "Diffuse urticaria and lip swelling after eating shellfish, mild wheezing, no stridor yet",
        "gold_esi": 2,
        "vitals": {"heart_rate": 112, "bp_systolic": 100, "bp_diastolic": 62, "spo2": 95, "temperature": 98.8, "respiratory_rate": 22},
        "age": 35, "comorbidities": ["asthma", "food_allergies"],
        "deterioration_threshold": 20,
        "required_tests": ["CBC"],
        "required_consults": [],
    },
    {
        "id": "esi2_overdose",
        "chief_complaint": "Found with empty pill bottles, drowsy but arousable, slurred speech, constricted pupils",
        "gold_esi": 2,
        "vitals": {"heart_rate": 58, "bp_systolic": 95, "bp_diastolic": 58, "spo2": 91, "temperature": 97.0, "respiratory_rate": 10},
        "age": 22, "comorbidities": ["depression"],
        "deterioration_threshold": 15,
        "required_tests": ["BMP", "CBC", "urinalysis"],
        "required_consults": ["psychiatry"],
    },
    {
        "id": "esi2_gi_hemorrhage",
        "chief_complaint": "Vomiting large amounts of bright red blood, 3 episodes in last hour, feeling faint",
        "gold_esi": 2,
        "vitals": {"heart_rate": 118, "bp_systolic": 92, "bp_diastolic": 55, "spo2": 96, "temperature": 98.4, "respiratory_rate": 20},
        "age": 52, "comorbidities": ["cirrhosis", "alcohol_use_disorder"],
        "deterioration_threshold": 15,
        "required_tests": ["CBC", "BMP", "blood_culture"],
        "required_consults": ["surgery"],
    },
    {
        "id": "esi2_severe_asthma",
        "chief_complaint": "Severe asthma attack, can only speak in single words, failed home nebulizer treatments three times",
        "gold_esi": 2,
        "vitals": {"heart_rate": 125, "bp_systolic": 140, "bp_diastolic": 88, "spo2": 89, "temperature": 98.6, "respiratory_rate": 32},
        "age": 19, "comorbidities": ["asthma", "eczema"],
        "deterioration_threshold": 15,
        "required_tests": ["CBC", "BMP"],
        "required_consults": ["pulmonology"],
    },
    {
        "id": "esi2_dka",
        "chief_complaint": "Extreme thirst, frequent urination, abdominal pain, fruity breath odor, confusion",
        "gold_esi": 2,
        "vitals": {"heart_rate": 115, "bp_systolic": 100, "bp_diastolic": 60, "spo2": 97, "temperature": 99.2, "respiratory_rate": 28},
        "age": 16, "comorbidities": ["type1_diabetes"],
        "deterioration_threshold": 20,
        "required_tests": ["BMP", "CBC", "urinalysis"],
        "required_consults": ["internal_medicine"],
    },
    {
        "id": "esi2_open_fracture",
        "chief_complaint": "Fall from ladder, bone protruding through skin of right lower leg, severe pain, bleeding",
        "gold_esi": 2,
        "vitals": {"heart_rate": 110, "bp_systolic": 135, "bp_diastolic": 80, "spo2": 98, "temperature": 98.6, "respiratory_rate": 22},
        "age": 45, "comorbidities": [],
        "deterioration_threshold": 30,
        "required_tests": ["X_ray", "CBC"],
        "required_consults": ["orthopedics"],
    },
    {
        "id": "esi2_acute_psychosis",
        "chief_complaint": "Agitated, hearing voices commanding self-harm, brought by police, actively trying to hurt self",
        "gold_esi": 2,
        "vitals": {"heart_rate": 105, "bp_systolic": 148, "bp_diastolic": 88, "spo2": 99, "temperature": 98.8, "respiratory_rate": 20},
        "age": 30, "comorbidities": ["schizophrenia"],
        "deterioration_threshold": 30,
        "required_tests": ["BMP", "CBC", "urinalysis"],
        "required_consults": ["psychiatry"],
    },
    {
        "id": "esi2_meningitis",
        "chief_complaint": "Severe headache, high fever, stiff neck, photophobia, petechial rash on trunk, confusion",
        "gold_esi": 2,
        "vitals": {"heart_rate": 120, "bp_systolic": 105, "bp_diastolic": 62, "spo2": 95, "temperature": 104.0, "respiratory_rate": 24},
        "age": 20, "comorbidities": [],
        "deterioration_threshold": 15,
        "required_tests": ["CBC", "BMP", "blood_culture"],
        "required_consults": ["internal_medicine"],
    },

    # ══════════════════════════════════════════════════════════════
    # ESI-3: URGENT — Requires 2+ resources (10 cases)
    # ══════════════════════════════════════════════════════════════
    {
        "id": "esi3_abdominal_pain",
        "chief_complaint": "Diffuse abdominal pain with nausea and vomiting for 12 hours, unable to tolerate fluids",
        "gold_esi": 3,
        "vitals": {"heart_rate": 98, "bp_systolic": 130, "bp_diastolic": 78, "spo2": 98, "temperature": 100.8, "respiratory_rate": 18},
        "age": 45, "comorbidities": ["gallstones"],
        "deterioration_threshold": 60,
        "required_tests": ["CBC", "BMP"],
        "required_consults": [],
    },
    {
        "id": "esi3_closed_fracture",
        "chief_complaint": "Obvious deformity left forearm after fall, moderate pain, unable to move wrist, no open wound",
        "gold_esi": 3,
        "vitals": {"heart_rate": 92, "bp_systolic": 140, "bp_diastolic": 82, "spo2": 99, "temperature": 98.6, "respiratory_rate": 18},
        "age": 12, "comorbidities": [],
        "deterioration_threshold": 90,
        "required_tests": ["X_ray"],
        "required_consults": ["orthopedics"],
    },
    {
        "id": "esi3_high_fever",
        "chief_complaint": "Fever of 103.5°F for 2 days, body aches, productive cough, did not respond to acetaminophen",
        "gold_esi": 3,
        "vitals": {"heart_rate": 102, "bp_systolic": 118, "bp_diastolic": 72, "spo2": 96, "temperature": 103.5, "respiratory_rate": 20},
        "age": 55, "comorbidities": ["diabetes"],
        "deterioration_threshold": 60,
        "required_tests": ["CBC", "blood_culture", "X_ray"],
        "required_consults": [],
    },
    {
        "id": "esi3_kidney_stone",
        "chief_complaint": "Sudden onset severe right flank pain radiating to groin, hematuria, writhing in pain, nauseous",
        "gold_esi": 3,
        "vitals": {"heart_rate": 100, "bp_systolic": 150, "bp_diastolic": 88, "spo2": 99, "temperature": 99.4, "respiratory_rate": 20},
        "age": 38, "comorbidities": ["kidney_stones_history"],
        "deterioration_threshold": 90,
        "required_tests": ["urinalysis", "BMP", "CT_chest"],
        "required_consults": [],
    },
    {
        "id": "esi3_deep_laceration",
        "chief_complaint": "Deep laceration to right hand from kitchen knife, visible tendon, moderate bleeding, intact sensation",
        "gold_esi": 3,
        "vitals": {"heart_rate": 88, "bp_systolic": 125, "bp_diastolic": 78, "spo2": 99, "temperature": 98.6, "respiratory_rate": 16},
        "age": 32, "comorbidities": [],
        "deterioration_threshold": 120,
        "required_tests": ["X_ray"],
        "required_consults": ["surgery"],
    },
    {
        "id": "esi3_pneumonia",
        "chief_complaint": "Productive cough with green sputum for 5 days, progressive dyspnea, chest pain with breathing",
        "gold_esi": 3,
        "vitals": {"heart_rate": 96, "bp_systolic": 122, "bp_diastolic": 74, "spo2": 93, "temperature": 102.2, "respiratory_rate": 24},
        "age": 70, "comorbidities": ["COPD", "heart_failure"],
        "deterioration_threshold": 45,
        "required_tests": ["CBC", "X_ray", "blood_culture"],
        "required_consults": ["pulmonology"],
    },
    {
        "id": "esi3_dvt",
        "chief_complaint": "Left calf swelling and pain for 2 days, redness and warmth, recently flew long-haul 10 hours",
        "gold_esi": 3,
        "vitals": {"heart_rate": 90, "bp_systolic": 128, "bp_diastolic": 80, "spo2": 97, "temperature": 99.0, "respiratory_rate": 16},
        "age": 48, "comorbidities": ["obesity", "oral_contraceptives"],
        "deterioration_threshold": 60,
        "required_tests": ["CBC", "BMP"],
        "required_consults": [],
    },
    {
        "id": "esi3_head_injury",
        "chief_complaint": "Hit head on shelf, brief loss of consciousness (30 seconds), vomited once, mild headache, oriented",
        "gold_esi": 3,
        "vitals": {"heart_rate": 78, "bp_systolic": 132, "bp_diastolic": 80, "spo2": 99, "temperature": 98.6, "respiratory_rate": 16},
        "age": 60, "comorbidities": ["anticoagulant_therapy"],
        "deterioration_threshold": 45,
        "required_tests": ["CT_head", "CBC"],
        "required_consults": ["neurology"],
    },
    {
        "id": "esi3_chest_pain_low",
        "chief_complaint": "Intermittent sharp chest pain for 6 hours, worse with deep breath, no radiation, no diaphoresis",
        "gold_esi": 3,
        "vitals": {"heart_rate": 82, "bp_systolic": 128, "bp_diastolic": 78, "spo2": 98, "temperature": 98.8, "respiratory_rate": 16},
        "age": 40, "comorbidities": ["anxiety"],
        "deterioration_threshold": 90,
        "required_tests": ["ECG", "troponin", "X_ray"],
        "required_consults": [],
    },
    {
        "id": "esi3_flank_pain_uti",
        "chief_complaint": "Right-sided flank pain, fever, painful urination, nausea, progressively worsening over 2 days",
        "gold_esi": 3,
        "vitals": {"heart_rate": 100, "bp_systolic": 125, "bp_diastolic": 75, "spo2": 98, "temperature": 102.0, "respiratory_rate": 18},
        "age": 28, "comorbidities": ["recurrent_UTI"],
        "deterioration_threshold": 60,
        "required_tests": ["urinalysis", "CBC", "BMP"],
        "required_consults": [],
    },

    # ══════════════════════════════════════════════════════════════
    # ESI-4: LESS URGENT — Requires 1 resource (10 cases)
    # ══════════════════════════════════════════════════════════════
    {
        "id": "esi4_simple_laceration",
        "chief_complaint": "Small cut on left hand from broken glass, minor bleeding controlled with pressure, no tendon involvement",
        "gold_esi": 4,
        "vitals": {"heart_rate": 78, "bp_systolic": 120, "bp_diastolic": 76, "spo2": 99, "temperature": 98.6, "respiratory_rate": 16},
        "age": 25, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_ankle_sprain",
        "chief_complaint": "Twisted right ankle while jogging, moderate swelling, able to bear weight with pain, no deformity",
        "gold_esi": 4,
        "vitals": {"heart_rate": 80, "bp_systolic": 122, "bp_diastolic": 74, "spo2": 99, "temperature": 98.4, "respiratory_rate": 14},
        "age": 30, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": ["X_ray"],
        "required_consults": [],
    },
    {
        "id": "esi4_uti_simple",
        "chief_complaint": "Burning with urination for 3 days, urinary frequency, mild lower abdominal discomfort, no fever",
        "gold_esi": 4,
        "vitals": {"heart_rate": 76, "bp_systolic": 118, "bp_diastolic": 72, "spo2": 99, "temperature": 99.0, "respiratory_rate": 14},
        "age": 32, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": ["urinalysis"],
        "required_consults": [],
    },
    {
        "id": "esi4_earache",
        "chief_complaint": "Right ear pain for 2 days, decreased hearing, no discharge, mild fever yesterday",
        "gold_esi": 4,
        "vitals": {"heart_rate": 82, "bp_systolic": 115, "bp_diastolic": 72, "spo2": 99, "temperature": 99.2, "respiratory_rate": 14},
        "age": 8, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_allergic_rash",
        "chief_complaint": "Itchy red rash on arms and torso after starting new detergent, no facial swelling, no breathing issues",
        "gold_esi": 4,
        "vitals": {"heart_rate": 74, "bp_systolic": 118, "bp_diastolic": 70, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 28, "comorbidities": ["eczema"],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_minor_head_bump",
        "chief_complaint": "Bumped head on cabinet door, small goose egg on forehead, no loss of consciousness, no vomiting",
        "gold_esi": 4,
        "vitals": {"heart_rate": 80, "bp_systolic": 120, "bp_diastolic": 76, "spo2": 99, "temperature": 98.6, "respiratory_rate": 15},
        "age": 5, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_sore_throat",
        "chief_complaint": "Sore throat and difficulty swallowing for 3 days, low-grade fever, white patches on tonsils",
        "gold_esi": 4,
        "vitals": {"heart_rate": 84, "bp_systolic": 116, "bp_diastolic": 74, "spo2": 99, "temperature": 100.2, "respiratory_rate": 15},
        "age": 18, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_eye_foreign_body",
        "chief_complaint": "Something flew into left eye while grinding metal, tearing, sensation of foreign body, vision intact",
        "gold_esi": 4,
        "vitals": {"heart_rate": 78, "bp_systolic": 125, "bp_diastolic": 78, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 35, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_minor_burn",
        "chief_complaint": "Burn to left forearm from hot oil while cooking, reddened area about 3cm diameter, painful, no blistering",
        "gold_esi": 4,
        "vitals": {"heart_rate": 82, "bp_systolic": 120, "bp_diastolic": 76, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 40, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi4_wrist_pain",
        "chief_complaint": "Wrist pain after catching self during fall on outstretched hand, mild swelling, can move fingers",
        "gold_esi": 4,
        "vitals": {"heart_rate": 76, "bp_systolic": 122, "bp_diastolic": 76, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 50, "comorbidities": ["osteoporosis"],
        "deterioration_threshold": None,
        "required_tests": ["X_ray"],
        "required_consults": [],
    },

    # ══════════════════════════════════════════════════════════════
    # ESI-5: NON-URGENT — No resources needed (10 cases)
    # ══════════════════════════════════════════════════════════════
    {
        "id": "esi5_common_cold",
        "chief_complaint": "Runny nose, mild cough and congestion for 4 days, no fever, eating and drinking normally",
        "gold_esi": 5,
        "vitals": {"heart_rate": 72, "bp_systolic": 118, "bp_diastolic": 72, "spo2": 99, "temperature": 98.4, "respiratory_rate": 14},
        "age": 30, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_rx_refill",
        "chief_complaint": "Ran out of blood pressure medication, pharmacy closed, needs refill of amlodipine 5mg",
        "gold_esi": 5,
        "vitals": {"heart_rate": 74, "bp_systolic": 138, "bp_diastolic": 86, "spo2": 99, "temperature": 98.4, "respiratory_rate": 14},
        "age": 60, "comorbidities": ["hypertension"],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_minor_rash",
        "chief_complaint": "Small dry patch of skin on elbow for 2 weeks, mild itching, no spreading, tried moisturizer",
        "gold_esi": 5,
        "vitals": {"heart_rate": 70, "bp_systolic": 115, "bp_diastolic": 70, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 35, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_chronic_knee",
        "chief_complaint": "Chronic bilateral knee pain, no recent injury, been present for months, wants evaluation",
        "gold_esi": 5,
        "vitals": {"heart_rate": 72, "bp_systolic": 130, "bp_diastolic": 82, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 62, "comorbidities": ["osteoarthritis", "obesity"],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_insect_bite",
        "chief_complaint": "Small red bump on forearm from mosquito bite yesterday, mild itching, no swelling, no streaking",
        "gold_esi": 5,
        "vitals": {"heart_rate": 70, "bp_systolic": 116, "bp_diastolic": 72, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 22, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_bruise",
        "chief_complaint": "Bruise on shin from bumping into coffee table 3 days ago, mildly tender, no swelling",
        "gold_esi": 5,
        "vitals": {"heart_rate": 68, "bp_systolic": 120, "bp_diastolic": 74, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 40, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_sunburn",
        "chief_complaint": "Mild sunburn on shoulders and back from beach yesterday, pink skin, tender to touch, no blisters",
        "gold_esi": 5,
        "vitals": {"heart_rate": 72, "bp_systolic": 118, "bp_diastolic": 72, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 26, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_suture_removal",
        "chief_complaint": "Here for suture removal from forehead laceration repaired 7 days ago, healing well, no redness",
        "gold_esi": 5,
        "vitals": {"heart_rate": 70, "bp_systolic": 120, "bp_diastolic": 76, "spo2": 99, "temperature": 98.6, "respiratory_rate": 14},
        "age": 44, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_med_question",
        "chief_complaint": "Wants to know if it is safe to take ibuprofen with current blood pressure medication",
        "gold_esi": 5,
        "vitals": {"heart_rate": 74, "bp_systolic": 132, "bp_diastolic": 80, "spo2": 99, "temperature": 98.4, "respiratory_rate": 14},
        "age": 56, "comorbidities": ["hypertension"],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
    {
        "id": "esi5_followup",
        "chief_complaint": "Follow-up visit for ankle sprain from 2 weeks ago, feels much better, wants clearance to run again",
        "gold_esi": 5,
        "vitals": {"heart_rate": 68, "bp_systolic": 118, "bp_diastolic": 72, "spo2": 99, "temperature": 98.4, "respiratory_rate": 14},
        "age": 28, "comorbidities": [],
        "deterioration_threshold": None,
        "required_tests": [],
        "required_consults": [],
    },
]


def calculate_severity_score(case: dict, vitals: dict, age: int) -> float:
    """
    Calculate a deterministic severity score from patient data.
    Higher score = more severe = should be triaged first.
    The agent never sees this score — it must infer severity from clinical information.
    """
    score = 0.0

    # Base ESI contribution (ESI 1 most severe)
    esi_base = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20}
    score += esi_base.get(case["gold_esi"], 0)

    # Heart rate
    hr = vitals.get("heart_rate", 80)
    if hr == 0:
        score += 30
    elif hr > 130:
        score += 20
    elif hr > 120:
        score += 15
    elif hr > 100:
        score += 8
    elif hr < 50:
        score += 15

    # Blood pressure
    sbp = vitals.get("bp_systolic", 120)
    if sbp < 80:
        score += 25
    elif sbp < 90:
        score += 20
    elif sbp < 100:
        score += 10
    elif sbp > 200:
        score += 15
    elif sbp > 180:
        score += 10

    # Oxygen saturation
    spo2 = vitals.get("spo2", 99)
    if spo2 < 80:
        score += 25
    elif spo2 < 88:
        score += 20
    elif spo2 < 92:
        score += 15
    elif spo2 < 95:
        score += 8

    # Temperature
    temp = vitals.get("temperature", 98.6)
    if temp > 104:
        score += 15
    elif temp > 103:
        score += 10
    elif temp > 101:
        score += 5

    # Respiratory rate
    rr = vitals.get("respiratory_rate", 16)
    if rr == 0:
        score += 30
    elif rr > 30:
        score += 15
    elif rr > 24:
        score += 10
    elif rr > 20:
        score += 5
    elif rr < 8:
        score += 20

    # Age risk
    if age > 75:
        score += 12
    elif age > 65:
        score += 8
    elif age > 55:
        score += 4
    elif age < 5:
        score += 12
    elif age < 18:
        score += 5

    # Comorbidities
    score += len(case.get("comorbidities", [])) * 3

    # Deterioration urgency
    thresh = case.get("deterioration_threshold")
    if thresh is not None:
        if thresh <= 5:
            score += 20
        elif thresh <= 15:
            score += 12
        elif thresh <= 30:
            score += 6

    return round(score, 2)
