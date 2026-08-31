import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { completeProfile ,getUserInfo } from "../services/userServices";

function FindSchemes() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    // ================= COMMON =================
    age: "",
    gender: "",
    state: "",
    district: "",
    marital_status: "",
    disability_status: null,
    annual_income: "",
    is_bpl: null,
    rural_urban: "",
    caste_category: "",
    loan_required: null,
    house_ownership: null,
    occupation: "",

    // ================= STUDENT =================
    education_level: "",
    course: "",
    year_of_study: "",
    institution_type: "",
    current_scholarship: null,

    // ================= FARMER =================
    land_owner: null,
    land_holding: "",
    farming_type: "",
    irrigation_available: null,
    agricultural_loan: null,

    // ================= BUSINESS =================
    business_type: "",
    business_registered: null,
    business_age: "",
    business_turnover: "",
    business_financial_need: null,

    // ================= HOMEMAKER =================
    skills: "",
    home_based_business: null,
    business_interest: null,
  });

  // =====================================================
  // STATES AND DISTRICTS
  // =====================================================

  const states = {
    Maharashtra: [
      "Pune",
      "Mumbai",
      "Nagpur",
      "Kolhapur",
      "Sangli",
    ],

    Gujarat: [
      "Ahmedabad",
      "Surat",
      "Vadodara",
    ],

    Karnataka: [
      "Bangalore",
      "Mysore",
      "Belgaum",
    ],

    Delhi: [
      "New Delhi",
      "North Delhi",
    ],
  };

  // =====================================================
  // UPDATE FIELD
  // =====================================================

  const updateField = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // =====================================================
  // TOTAL QUESTIONS
  // =====================================================

  const getTotalQuestions = () => {
    if (formData.occupation === "Student") {
      return 18;
    }

    if (formData.occupation === "Farmer") {
      return 18;
    }

    if (
      formData.occupation ===
      "Business Owner / Self-employed"
    ) {
      return 18;
    }

    if (formData.occupation === "Homemaker") {
      return 17;
    }

    return 13;
  };

  const totalQuestions = getTotalQuestions();

  const progress = Math.min(
    (Math.min(step, totalQuestions) / totalQuestions) * 100,
    100
  );

  // =====================================================
  // VALIDATE COMMON QUESTIONS
  // =====================================================

  const validateCurrentStep = () => {
    switch (step) {
      case 1:
        return formData.age !== "";

      case 2:
        return formData.gender !== "";

      case 3:
        return formData.state !== "";

      case 4:
        return formData.district !== "";

      case 5:
        return formData.marital_status !== "";

      case 6:
        return formData.disability_status !== null;

      case 7:
        return formData.annual_income !== "";

      case 8:
        return formData.is_bpl !== null;

      case 9:
        return formData.rural_urban !== "";

      case 10:
        return formData.caste_category !== "";

      case 11:
        return formData.loan_required !== null;

      case 12:
        return formData.house_ownership !== null;

      case 13:
        return formData.occupation !== "";

      default:
        return true;
    }
  };

  // =====================================================
  // VALIDATE OCCUPATION QUESTIONS
  // =====================================================

  const validateConditionalStep = () => {
    // ================= STUDENT =================

    if (formData.occupation === "Student") {
      if (step === 14) {
        return formData.education_level !== "";
      }

      if (step === 15) {
        return formData.course !== "";
      }

      if (step === 16) {
        return formData.year_of_study !== "";
      }

      if (step === 17) {
        return formData.institution_type !== "";
      }

      if (step === 18) {
        return formData.current_scholarship !== null;
      }
    }

    // ================= FARMER =================

    if (formData.occupation === "Farmer") {
      if (step === 14) {
        return formData.land_owner !== null;
      }

      if (step === 15) {
        return formData.land_holding !== "";
      }

      if (step === 16) {
        return formData.farming_type !== "";
      }

      if (step === 17) {
        return formData.irrigation_available !== null;
      }

      if (step === 18) {
        return formData.agricultural_loan !== null;
      }
    }

    // ================= BUSINESS =================

    if (
      formData.occupation ===
      "Business Owner / Self-employed"
    ) {
      if (step === 14) {
        return formData.business_type !== "";
      }

      if (step === 15) {
        return formData.business_registered !== null;
      }

      if (step === 16) {
        return formData.business_age !== "";
      }

      if (step === 17) {
        return formData.business_turnover !== "";
      }

      if (step === 18) {
        return formData.business_financial_need !== null;
      }
    }

    // ================= HOMEMAKER =================

    if (formData.occupation === "Homemaker") {
      if (step === 14) {
        return formData.education_level !== "";
      }

      if (step === 15) {
        return formData.skills !== "";
      }

      if (step === 16) {
        return formData.home_based_business !== null;
      }

      if (step === 17) {
        return formData.business_interest !== null;
      }
    }

    return true;
  };

  // =====================================================
  // NEXT STEP
  // =====================================================

  const nextStep = () => {
    if (step <= 13) {
      if (!validateCurrentStep()) {
        alert("Please answer this question.");
        return;
      }
    }

    if (step >= 14) {
      if (!validateConditionalStep()) {
        alert("Please answer this question.");
        return;
      }
    }

    // After occupation question
    if (step === 13) {
      if (formData.occupation === "Other") {
        setStep(19);
      } else {
        setStep(14);
      }

      return;
    }

    // Student / Farmer / Business
    if (
      step === 18 &&
      (
        formData.occupation === "Student" ||
        formData.occupation === "Farmer" ||
        formData.occupation ===
          "Business Owner / Self-employed"
      )
    ) {
      setStep(19);
      return;
    }

    // Homemaker
    if (
      step === 17 &&
      formData.occupation === "Homemaker"
    ) {
      setStep(19);
      return;
    }

    setStep((prev) => prev + 1);
  };

  // =====================================================
  // PREVIOUS STEP
  // =====================================================

  const previousStep = () => {
    if (step === 19) {
      if (formData.occupation === "Other") {
        setStep(13);
      } else if (formData.occupation === "Homemaker") {
        setStep(17);
      } else {
        setStep(18);
      }

      return;
    }

    setStep((prev) => Math.max(prev - 1, 1));
  };

  // =====================================================
  // SUBMIT PROFILE
  // =====================================================

  const handleSubmit = async () => {
    if (submitting) return;

    try {
      setSubmitting(true);

      /*
       * IMPORTANT FIX
       *
       * Your frontend questionnaire uses:
       *
       * annual_income
       * caste_category
       *
       * But your existing backend/profile structure
       * uses:
       *
       * income
       * category
       *
       * Therefore we create a backend-compatible
       * payload here.
       */

      const profileData = {
        // ================= EXISTING BACKEND FIELDS =================

        age: formData.age,
        gender: formData.gender,

        // FIX:
        annual_income: formData.annual_income,

        // FIX:
        caste_category: formData.caste_category,

        state: formData.state,
        occupation: formData.occupation,
        education_level: formData.education_level,

        // ================= ADDITIONAL QUESTIONNAIRE FIELDS =================

        district: formData.district,
        marital_status: formData.marital_status,
        disability_status: formData.disability_status,
        is_bpl: formData.is_bpl,
        rural_urban: formData.rural_urban,
        loan_required: formData.loan_required,
        house_ownership: formData.house_ownership,

        // ================= STUDENT =================

        course: formData.course,
        year_of_study: formData.year_of_study,
        institution_type: formData.institution_type,
        current_scholarship:
          formData.current_scholarship,

        // ================= FARMER =================

        land_owner: formData.land_owner,
        land_holding: formData.land_holding,
        farming_type: formData.farming_type,
        irrigation_available:
          formData.irrigation_available,
        agricultural_loan:
          formData.agricultural_loan,

        // ================= BUSINESS =================

        business_type: formData.business_type,
        business_registered:
          formData.business_registered,
        business_age: formData.business_age,
        business_turnover:
          formData.business_turnover,
        business_financial_need:
          formData.business_financial_need,

        // ================= HOMEMAKER =================

        skills: formData.skills,
        home_based_business:
          formData.home_based_business,
        business_interest:
          formData.business_interest,
      };

      console.log(
        "QUESTIONNAIRE DATA:",
        formData
      );

      console.log(
        "BACKEND PROFILE DATA:",
        profileData
      );

      const result = await completeProfile(
        profileData
      );

      console.log(
        "PROFILE API RESPONSE:",
        result
      );

      if (result?.status === "success") {
  console.log("Profile saved successfully");

  // Get fresh profile from backend
  const freshProfile = await getUserInfo();

  console.log("FRESH PROFILE:", freshProfile);

  alert("Profile completed successfully!");

  navigate("/recommendation-start", {
    replace: true,
    state: {
      profile: freshProfile?.data,
    },
  });

      } else {
        alert(
          result?.error ||
            result?.message ||
            "Failed to save profile."
        );
      }
    } catch (error) {
      console.error(
        "PROFILE API ERROR:",
        error
      );

      alert(
        error?.message ||
          "Something went wrong while saving your profile."
      );
    } finally {
      setSubmitting(false);
    }
  };

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <div style={styles.container}>

      <h1 style={styles.heading}>
        Find Government Schemes
      </h1>

      <p style={styles.subtitle}>
        Answer a few questions to find government
        schemes you may be eligible for.
      </p>

      {/* ================= PROGRESS ================= */}

      <div style={styles.progressContainer}>
        <div
          style={{
            ...styles.progressBar,
            width: `${progress}%`,
          }}
        />
      </div>

      <p style={styles.progressText}>
        {step === 19
          ? "Review your answers"
          : `Question ${step} of ${totalQuestions}`}
      </p>

      {/* ================= COMMON QUESTIONS ================= */}

      {/* 1. AGE */}

      {step === 1 && (
        <Question title="What is your age?">
          <input
            type="number"
            min="1"
            max="120"
            value={formData.age}
            onChange={(e) =>
              updateField(
                "age",
                e.target.value
              )
            }
            placeholder="Enter your age"
            style={styles.input}
          />
        </Question>
      )}

      {/* 2. GENDER */}

      {step === 2 && (
        <Question title="What is your gender?">
          <select
            value={formData.gender}
            onChange={(e) =>
              updateField(
                "gender",
                e.target.value
              )
            }
            style={styles.input}
          >
            <option value="">
              Select gender
            </option>

            <option value="Male">
              Male
            </option>

            <option value="Female">
              Female
            </option>

            <option value="Other">
              Other
            </option>
          </select>
        </Question>
      )}

      {/* 3. STATE */}

      {step === 3 && (
        <Question title="Which state do you live in?">
          <select
            value={formData.state}
            onChange={(e) => {
              updateField(
                "state",
                e.target.value
              );

              updateField(
                "district",
                ""
              );
            }}
            style={styles.input}
          >
            <option value="">
              Select state
            </option>

            {Object.keys(states).map(
              (state) => (
                <option
                  key={state}
                  value={state}
                >
                  {state}
                </option>
              )
            )}
          </select>
        </Question>
      )}

      {/* 4. DISTRICT */}

      {step === 4 && (
        <Question title="Which district do you live in?">
          <select
            value={formData.district}
            onChange={(e) =>
              updateField(
                "district",
                e.target.value
              )
            }
            style={styles.input}
            disabled={!formData.state}
          >
            <option value="">
              Select district
            </option>

            {formData.state &&
              states[formData.state]?.map(
                (district) => (
                  <option
                    key={district}
                    value={district}
                  >
                    {district}
                  </option>
                )
              )}
          </select>
        </Question>
      )}

      {/* 5. MARITAL STATUS */}

      {step === 5 && (
        <Question title="What is your marital status?">
          <select
            value={formData.marital_status}
            onChange={(e) =>
              updateField(
                "marital_status",
                e.target.value
              )
            }
            style={styles.input}
          >
            <option value="">
              Select status
            </option>

            <option value="Single">
              Single
            </option>

            <option value="Married">
              Married
            </option>

            <option value="Widowed">
              Widowed
            </option>

            <option value="Divorced">
              Divorced
            </option>

            <option value="Separated">
              Separated
            </option>
          </select>
        </Question>
      )}

      {/* 6. DISABILITY */}

      {step === 6 && (
        <Question title="Do you have any disability?">
          <YesNo
            value={formData.disability_status}
            onChange={(value) =>
              updateField(
                "disability_status",
                value
              )
            }
          />
        </Question>
      )}

      {/* 7. INCOME */}

      {step === 7 && (
        <Question title="What is your annual family income?">
          <input
            type="number"
            min="0"
            value={formData.annual_income}
            onChange={(e) =>
              updateField(
                "annual_income",
                e.target.value
              )
            }
            placeholder="Enter annual income"
            style={styles.input}
          />
        </Question>
      )}

      {/* 8. BPL */}

      {step === 8 && (
        <Question title="Do you belong to a BPL household?">
          <YesNo
            value={formData.is_bpl}
            onChange={(value) =>
              updateField(
                "is_bpl",
                value
              )
            }
          />
        </Question>
      )}

      {/* 9. RURAL / URBAN */}

      {step === 9 && (
        <Question title="Do you live in a rural or urban area?">
          <select
            value={formData.rural_urban}
            onChange={(e) =>
              updateField(
                "rural_urban",
                e.target.value
              )
            }
            style={styles.input}
          >
            <option value="">
              Select area
            </option>

            <option value="Rural">
              Rural
            </option>

            <option value="Urban">
              Urban
            </option>
          </select>
        </Question>
      )}

      {/* 10. CASTE */}

      {step === 10 && (
        <Question title="What is your caste category?">
          <select
            value={formData.caste_category}
            onChange={(e) =>
              updateField(
                "caste_category",
                e.target.value
              )
            }
            style={styles.input}
          >
            <option value="">
              Select category
            </option>

            <option value="General">
              General
            </option>

            <option value="OBC">
              OBC
            </option>

            <option value="SC">
              SC
            </option>

            <option value="ST">
              ST
            </option>

            <option value="EWS">
              EWS
            </option>
          </select>
        </Question>
      )}

      {/* 11. LOAN */}

      {step === 11 && (
        <Question title="Are you looking for a loan or financial assistance?">
          <YesNo
            value={formData.loan_required}
            onChange={(value) =>
              updateField(
                "loan_required",
                value
              )
            }
          />
        </Question>
      )}

      {/* 12. HOUSE */}

      {step === 12 && (
        <Question title="Do you own a house?">
          <YesNo
            value={formData.house_ownership}
            onChange={(value) =>
              updateField(
                "house_ownership",
                value
              )
            }
          />
        </Question>
      )}

      {/* 13. OCCUPATION */}

      {step === 13 && (
        <Question title="What is your current occupation?">
          <select
            value={formData.occupation}
            onChange={(e) =>
              updateField(
                "occupation",
                e.target.value
              )
            }
            style={styles.input}
          >
            <option value="">
              Select occupation
            </option>

            <option value="Student">
              Student
            </option>

            <option value="Farmer">
              Farmer
            </option>

            <option value="Business Owner / Self-employed">
              Business Owner / Self-employed
            </option>

            <option value="Homemaker">
              Homemaker
            </option>

            <option value="Other">
              Other
            </option>
          </select>
        </Question>
      )}

      {/* ================= STUDENT ================= */}

      {formData.occupation === "Student" &&
        step === 14 && (
          <Question title="What is your education level?">
            <select
              value={formData.education_level}
              onChange={(e) =>
                updateField(
                  "education_level",
                  e.target.value
                )
              }
              style={styles.input}
            >
              <option value="">
                Select education level
              </option>

              <option value="School">
                School
              </option>

              <option value="Diploma">
                Diploma
              </option>

              <option value="Undergraduate">
                Undergraduate
              </option>

              <option value="Postgraduate">
                Postgraduate
              </option>
            </select>
          </Question>
        )}

      {formData.occupation === "Student" &&
        step === 15 && (
          <Question title="What course are you pursuing?">
            <input
              type="text"
              value={formData.course}
              onChange={(e) =>
                updateField(
                  "course",
                  e.target.value
                )
              }
              placeholder="Enter course"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation === "Student" &&
        step === 16 && (
          <Question title="Which year or standard are you studying in?">
            <input
              type="text"
              value={formData.year_of_study}
              onChange={(e) =>
                updateField(
                  "year_of_study",
                  e.target.value
                )
              }
              placeholder="Enter year or standard"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation === "Student" &&
        step === 17 && (
          <Question title="What type of institution do you attend?">
            <select
              value={formData.institution_type}
              onChange={(e) =>
                updateField(
                  "institution_type",
                  e.target.value
                )
              }
              style={styles.input}
            >
              <option value="">
                Select institution type
              </option>

              <option value="Government">
                Government
              </option>

              <option value="Private">
                Private
              </option>
            </select>
          </Question>
        )}

      {formData.occupation === "Student" &&
        step === 18 && (
          <Question title="Are you receiving any scholarship?">
            <YesNo
              value={formData.current_scholarship}
              onChange={(value) =>
                updateField(
                  "current_scholarship",
                  value
                )
              }
            />
          </Question>
        )}

      {/* ================= FARMER ================= */}

      {formData.occupation === "Farmer" &&
        step === 14 && (
          <Question title="Do you own agricultural land?">
            <YesNo
              value={formData.land_owner}
              onChange={(value) =>
                updateField(
                  "land_owner",
                  value
                )
              }
            />
          </Question>
        )}

      {formData.occupation === "Farmer" &&
        step === 15 && (
          <Question title="How much agricultural land do you own?">
            <input
              type="number"
              min="0"
              value={formData.land_holding}
              onChange={(e) =>
                updateField(
                  "land_holding",
                  e.target.value
                )
              }
              placeholder="Enter land size"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation === "Farmer" &&
        step === 16 && (
          <Question title="What type of farming do you mainly do?">
            <input
              type="text"
              value={formData.farming_type}
              onChange={(e) =>
                updateField(
                  "farming_type",
                  e.target.value
                )
              }
              placeholder="Enter farming type"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation === "Farmer" &&
        step === 17 && (
          <Question title="Do you have access to irrigation?">
            <YesNo
              value={formData.irrigation_available}
              onChange={(value) =>
                updateField(
                  "irrigation_available",
                  value
                )
              }
            />
          </Question>
        )}

      {formData.occupation === "Farmer" &&
        step === 18 && (
          <Question title="Do you have an agricultural loan?">
            <YesNo
              value={formData.agricultural_loan}
              onChange={(value) =>
                updateField(
                  "agricultural_loan",
                  value
                )
              }
            />
          </Question>
        )}

      {/* ================= BUSINESS ================= */}

      {formData.occupation ===
        "Business Owner / Self-employed" &&
        step === 14 && (
          <Question title="What type of business do you operate?">
            <input
              type="text"
              value={formData.business_type}
              onChange={(e) =>
                updateField(
                  "business_type",
                  e.target.value
                )
              }
              placeholder="Enter business type"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation ===
        "Business Owner / Self-employed" &&
        step === 15 && (
          <Question title="Is your business registered?">
            <YesNo
              value={formData.business_registered}
              onChange={(value) =>
                updateField(
                  "business_registered",
                  value
                )
              }
            />
          </Question>
        )}

      {formData.occupation ===
        "Business Owner / Self-employed" &&
        step === 16 && (
          <Question title="How long has your business been operating?">
            <input
              type="number"
              min="0"
              value={formData.business_age}
              onChange={(e) =>
                updateField(
                  "business_age",
                  e.target.value
                )
              }
              placeholder="Years"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation ===
        "Business Owner / Self-employed" &&
        step === 17 && (
          <Question title="What is your annual business turnover?">
            <input
              type="number"
              min="0"
              value={formData.business_turnover}
              onChange={(e) =>
                updateField(
                  "business_turnover",
                  e.target.value
                )
              }
              placeholder="Enter annual turnover"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation ===
        "Business Owner / Self-employed" &&
        step === 18 && (
          <Question title="Are you looking for business financial assistance?">
            <YesNo
              value={formData.business_financial_need}
              onChange={(value) =>
                updateField(
                  "business_financial_need",
                  value
                )
              }
            />
          </Question>
        )}

      {/* ================= HOMEMAKER ================= */}

      {formData.occupation === "Homemaker" &&
        step === 14 && (
          <Question title="What is your highest education level?">
            <select
              value={formData.education_level}
              onChange={(e) =>
                updateField(
                  "education_level",
                  e.target.value
                )
              }
              style={styles.input}
            >
              <option value="">
                Select education level
              </option>

              <option value="School">
                School
              </option>

              <option value="Diploma">
                Diploma
              </option>

              <option value="Undergraduate">
                Undergraduate
              </option>

              <option value="Postgraduate">
                Postgraduate
              </option>
            </select>
          </Question>
        )}

      {formData.occupation === "Homemaker" &&
        step === 15 && (
          <Question title="Do you have any vocational or professional skills?">
            <input
              type="text"
              value={formData.skills}
              onChange={(e) =>
                updateField(
                  "skills",
                  e.target.value
                )
              }
              placeholder="Enter your skills"
              style={styles.input}
            />
          </Question>
        )}

      {formData.occupation === "Homemaker" &&
        step === 16 && (
          <Question title="Do you run a home-based business or activity?">
            <YesNo
              value={formData.home_based_business}
              onChange={(value) =>
                updateField(
                  "home_based_business",
                  value
                )
              }
            />
          </Question>
        )}

      {formData.occupation === "Homemaker" &&
        step === 17 && (
          <Question title="Are you interested in starting a business?">
            <YesNo
              value={formData.business_interest}
              onChange={(value) =>
                updateField(
                  "business_interest",
                  value
                )
              }
            />
          </Question>
        )}

      {/* ================= REVIEW ================= */}

      {step === 19 && (
        <Review
          formData={formData}
          onSubmit={handleSubmit}
          submitting={submitting}
        />
      )}

      {/* ================= NAVIGATION ================= */}

      {step !== 19 && (
        <div style={styles.buttonContainer}>

          {step > 1 && (
            <button
              style={styles.backButton}
              onClick={previousStep}
              disabled={submitting}
            >
              Back
            </button>
          )}

          <button
            style={styles.nextButton}
            onClick={nextStep}
            disabled={submitting}
          >
            Next
          </button>

        </div>
      )}
    </div>
  );
}

// =====================================================
// QUESTION COMPONENT
// =====================================================

function Question({ title, children }) {
  return (
    <div>
      <h2 style={styles.question}>
        {title}
      </h2>

      {children}
    </div>
  );
}

// =====================================================
// YES / NO COMPONENT
// =====================================================

function YesNo({ value, onChange }) {
  return (
    <div style={styles.yesNoContainer}>

      <button
        type="button"
        style={{
          ...styles.optionButton,
          ...(value === true
            ? styles.selectedButton
            : {}),
        }}
        onClick={() => onChange(true)}
      >
        Yes
      </button>

      <button
        type="button"
        style={{
          ...styles.optionButton,
          ...(value === false
            ? styles.selectedButton
            : {}),
        }}
        onClick={() => onChange(false)}
      >
        No
      </button>

    </div>
  );
}

// =====================================================
// REVIEW COMPONENT
// =====================================================

function Review({
  formData,
  onSubmit,
  submitting,
}) {
  const displayBoolean = (value) => {
    if (value === true) return "Yes";
    if (value === false) return "No";
    return "Not answered";
  };

  return (
    <div>

      <h2 style={styles.question}>
        Review your answers
      </h2>

      <div style={styles.reviewBox}>

        <p>
          <strong>Age:</strong>{" "}
          {formData.age}
        </p>

        <p>
          <strong>Gender:</strong>{" "}
          {formData.gender}
        </p>

        <p>
          <strong>State:</strong>{" "}
          {formData.state}
        </p>

        <p>
          <strong>District:</strong>{" "}
          {formData.district}
        </p>

        <p>
          <strong>Marital Status:</strong>{" "}
          {formData.marital_status}
        </p>

        <p>
          <strong>Disability:</strong>{" "}
          {displayBoolean(
            formData.disability_status
          )}
        </p>

        <p>
          <strong>Annual Income:</strong>{" "}
          ₹{formData.annual_income}
        </p>

        <p>
          <strong>BPL:</strong>{" "}
          {displayBoolean(formData.is_bpl)}
        </p>

        <p>
          <strong>Area:</strong>{" "}
          {formData.rural_urban}
        </p>

        <p>
          <strong>Caste:</strong>{" "}
          {formData.caste_category}
        </p>

        <p>
          <strong>Loan Required:</strong>{" "}
          {displayBoolean(
            formData.loan_required
          )}
        </p>

        <p>
          <strong>House Ownership:</strong>{" "}
          {displayBoolean(
            formData.house_ownership
          )}
        </p>

        <p>
          <strong>Occupation:</strong>{" "}
          {formData.occupation}
        </p>

        {/* STUDENT */}

        {formData.occupation === "Student" && (
          <>
            <p>
              <strong>Education:</strong>{" "}
              {formData.education_level}
            </p>

            <p>
              <strong>Course:</strong>{" "}
              {formData.course}
            </p>

            <p>
              <strong>Year of Study:</strong>{" "}
              {formData.year_of_study}
            </p>

            <p>
              <strong>Institution:</strong>{" "}
              {formData.institution_type}
            </p>

            <p>
              <strong>Current Scholarship:</strong>{" "}
              {displayBoolean(
                formData.current_scholarship
              )}
            </p>
          </>
        )}

        {/* FARMER */}

        {formData.occupation === "Farmer" && (
          <>
            <p>
              <strong>Land Owner:</strong>{" "}
              {displayBoolean(
                formData.land_owner
              )}
            </p>

            <p>
              <strong>Land Holding:</strong>{" "}
              {formData.land_holding}
            </p>

            <p>
              <strong>Farming Type:</strong>{" "}
              {formData.farming_type}
            </p>

            <p>
              <strong>Irrigation:</strong>{" "}
              {displayBoolean(
                formData.irrigation_available
              )}
            </p>

            <p>
              <strong>Agricultural Loan:</strong>{" "}
              {displayBoolean(
                formData.agricultural_loan
              )}
            </p>
          </>
        )}

        {/* BUSINESS */}

        {formData.occupation ===
          "Business Owner / Self-employed" && (
          <>
            <p>
              <strong>Business Type:</strong>{" "}
              {formData.business_type}
            </p>

            <p>
              <strong>Business Registered:</strong>{" "}
              {displayBoolean(
                formData.business_registered
              )}
            </p>

            <p>
              <strong>Business Age:</strong>{" "}
              {formData.business_age}
            </p>

            <p>
              <strong>Business Turnover:</strong>{" "}
              ₹{formData.business_turnover}
            </p>

            <p>
              <strong>Financial Assistance:</strong>{" "}
              {displayBoolean(
                formData.business_financial_need
              )}
            </p>
          </>
        )}

        {/* HOMEMAKER */}

        {formData.occupation === "Homemaker" && (
          <>
            <p>
              <strong>Education:</strong>{" "}
              {formData.education_level}
            </p>

            <p>
              <strong>Skills:</strong>{" "}
              {formData.skills}
            </p>

            <p>
              <strong>Home Based Business:</strong>{" "}
              {displayBoolean(
                formData.home_based_business
              )}
            </p>

            <p>
              <strong>Business Interest:</strong>{" "}
              {displayBoolean(
                formData.business_interest
              )}
            </p>
          </>
        )}

      </div>

      <button
        style={{
          ...styles.submitButton,
          opacity: submitting ? 0.6 : 1,
        }}
        onClick={onSubmit}
        disabled={submitting}
      >
        {submitting
          ? "Saving Profile..."
          : "Complete Profile"}
      </button>

    </div>
  );
}

// =====================================================
// STYLES
// =====================================================

const styles = {
  container: {
    maxWidth: "650px",
    margin: "40px auto",
    padding: "30px",
    borderRadius: "12px",
    backgroundColor: "#ffffff",
    boxShadow: "0 0 15px rgba(0,0,0,0.1)",
    fontFamily: "Arial",
  },

  heading: {
    textAlign: "center",
    marginBottom: "8px",
  },

  subtitle: {
    textAlign: "center",
    color: "#666",
    marginBottom: "25px",
  },

  progressContainer: {
    width: "100%",
    height: "8px",
    backgroundColor: "#e5e7eb",
    borderRadius: "10px",
    marginBottom: "8px",
  },

  progressBar: {
    height: "100%",
    backgroundColor: "#2563eb",
    borderRadius: "10px",
    transition: "width 0.3s ease",
  },

  progressText: {
    textAlign: "right",
    color: "#666",
    fontSize: "13px",
  },

  question: {
    marginTop: "35px",
    marginBottom: "20px",
    fontSize: "23px",
  },

  input: {
    width: "100%",
    padding: "13px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "15px",
    boxSizing: "border-box",
  },

  yesNoContainer: {
    display: "flex",
    gap: "15px",
  },

  optionButton: {
    flex: 1,
    padding: "13px",
    border: "1px solid #ccc",
    borderRadius: "8px",
    backgroundColor: "#fff",
    cursor: "pointer",
    fontSize: "15px",
  },

  selectedButton: {
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "1px solid #2563eb",
  },

  buttonContainer: {
    display: "flex",
    justifyContent: "space-between",
    marginTop: "35px",
  },

  nextButton: {
    padding: "12px 25px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },

  backButton: {
    padding: "12px 25px",
    backgroundColor: "#6b7280",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },

  submitButton: {
    width: "100%",
    padding: "13px",
    marginTop: "20px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
  },

  reviewBox: {
    backgroundColor: "#f9fafb",
    padding: "20px",
    borderRadius: "10px",
    marginTop: "20px",
    lineHeight: "1.7",
  },
};

export default FindSchemes;