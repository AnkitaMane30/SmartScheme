import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserInfo, updateUserInfo } from "../services/userServices";

function UpdateProfile() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    // ================= COMMON =================
    age: "",
    gender: "",
    state: "Maharashtra",
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
  // MAHARASHTRA DISTRICTS (Complete list)
  // =====================================================

  const maharashtraDistricts = [
    "Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed",
    "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli",
    "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
    "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded",
    "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani",
    "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara",
    "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
  ];

  // =====================================================
  // DROPDOWN OPTIONS (same as FindSchemes)
  // =====================================================

  const educationOptions = [
    "10th", "12th", "Diploma", "Undergraduate", "Postgraduate", "Illiterate", "Other"
  ];

  const courseOptions = [
    "B.Tech / B.E", "B.Sc", "B.Com", "B.A", "BBA", "BCA",
    "M.Tech", "MBA", "M.Sc", "M.Com", "Diploma", "ITI", "Other"
  ];

  const yearOfStudyOptions = [
    "1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year",
    "Class 1-5", "Class 6-8", "Class 9-10", "Class 11", "Class 12", "Other"
  ];

  const farmingTypeOptions = [
    "Crop Farming", "Horticulture", "Dairy", "Poultry",
    "Fisheries", "Mixed Farming", "Organic Farming", "Other"
  ];

  const businessTypeOptions = [
    "Retail Shop", "Manufacturing", "Service", "Trading",
    "Food Business", "Handicraft", "IT / Software", "Other"
  ];

  const skillsOptions = [
    "Tailoring / Stitching", "Cooking / Catering", "Beauty & Wellness",
    "Handicraft", "Computer Skills", "Teaching", "Embroidery", "Other"
  ];

  // ============================================================
  // CONVERT BACKEND BOOLEAN VALUES
  // ============================================================

  const convertBoolean = (value) => {
    if (value === true || value === 1 || value === "1") {
      return true;
    }

    if (value === false || value === 0 || value === "0") {
      return false;
    }

    if (typeof value === "string") {
      const lower = value.toLowerCase();

      if (lower === "true" || lower === "yes") {
        return true;
      }

      if (lower === "false" || lower === "no") {
        return false;
      }
    }

    return null;
  };

  // ============================================================
  // FETCH EXISTING USER DATA
  // ============================================================

  useEffect(() => {
    const loadUserInfo = async () => {
      try {
        setLoading(true);

        const result = await getUserInfo();

        console.log("USER INFO RESPONSE:", result);

        if (result.status !== "success") {
          alert(result.error || "Unable to load your profile.");
          navigate("/recommendation-start");
          return;
        }

        const data = result.data;

        console.log("PROFILE DATA:", data);

        setFormData({
          // ================= COMMON =================
          age: data.age ?? "",
          gender: data.gender ?? "",
          state: "Maharashtra",
          district: data.district ?? "",
          marital_status: data.marital_status ?? "",
          disability_status: convertBoolean(data.disability_status),
          annual_income: data.annual_income ?? "",
          is_bpl: convertBoolean(data.is_bpl),
          rural_urban: data.rural_urban ?? "",
          caste_category: data.caste_category ?? "",
          loan_required: convertBoolean(data.loan_required),
          house_ownership: convertBoolean(data.house_ownership),
          occupation: data.occupation ?? "",

          // ================= STUDENT =================
          education_level: data.education_level ?? "",
          course: data.course ?? "",
          year_of_study: data.year_of_study ?? "",
          institution_type: data.institution_type ?? "",
          current_scholarship: convertBoolean(data.current_scholarship),

          // ================= FARMER =================
          land_owner: convertBoolean(data.land_owner),
          land_holding: data.land_holding ?? "",
          farming_type: data.farming_type ?? "",
          irrigation_available: convertBoolean(data.irrigation_available),
          agricultural_loan: convertBoolean(data.agricultural_loan),

          // ================= BUSINESS =================
          business_type: data.business_type ?? "",
          business_registered: convertBoolean(data.business_registered),
          business_age: data.business_age ?? "",
          business_turnover: data.business_turnover ?? "",
          business_financial_need: convertBoolean(data.business_financial_need),

          // ================= HOMEMAKER =================
          skills: data.skills ?? "",
          home_based_business: convertBoolean(data.home_based_business),
          business_interest: convertBoolean(data.business_interest),
        });
      } catch (error) {
        console.error("LOAD PROFILE ERROR:", error);
        alert(
          error.message ||
            "Something went wrong while loading your profile."
        );
      } finally {
        setLoading(false);
      }
    };

    loadUserInfo();
  }, [navigate]);

  // ============================================================
  // UPDATE FIELD
  // ============================================================

  const updateField = (field, value) => {
    setFormData((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  // ============================================================
  // VALIDATION
  // ============================================================

  const validateForm = () => {
    const commonFields = {
      age: formData.age,
      gender: formData.gender,
      state: formData.state,
      district: formData.district,
      marital_status: formData.marital_status,
      disability_status: formData.disability_status,
      annual_income: formData.annual_income,
      is_bpl: formData.is_bpl,
      rural_urban: formData.rural_urban,
      caste_category: formData.caste_category,
      loan_required: formData.loan_required,
      house_ownership: formData.house_ownership,
      occupation: formData.occupation,
    };

    for (const [field, value] of Object.entries(commonFields)) {
      if (value === null || value === undefined || value === "") {
        alert(`Please provide ${formatFieldName(field)}.`);
        return false;
      }
    }

    if (formData.occupation === "Student") {
      const fields = {
        education_level: formData.education_level,
        course: formData.course,
        year_of_study: formData.year_of_study,
        institution_type: formData.institution_type,
        current_scholarship: formData.current_scholarship,
      };
      return validateFields(fields);
    }

    if (formData.occupation === "Farmer") {
      const fields = {
        land_owner: formData.land_owner,
        land_holding: formData.land_holding,
        farming_type: formData.farming_type,
        irrigation_available: formData.irrigation_available,
        agricultural_loan: formData.agricultural_loan,
      };
      return validateFields(fields);
    }

    if (formData.occupation === "Business Owner / Self-employed") {
      const fields = {
        business_type: formData.business_type,
        business_registered: formData.business_registered,
        business_age: formData.business_age,
        business_turnover: formData.business_turnover,
        business_financial_need: formData.business_financial_need,
      };
      return validateFields(fields);
    }

    if (formData.occupation === "Homemaker") {
      const fields = {
        education_level: formData.education_level,
        skills: formData.skills,
        home_based_business: formData.home_based_business,
        business_interest: formData.business_interest,
      };
      return validateFields(fields);
    }

    if (formData.occupation === "Other") {
      return true;
    }

    alert("Invalid occupation.");
    return false;
  };

  // ============================================================
  // VALIDATE FIELD GROUP
  // ============================================================

  const validateFields = (fields) => {
    for (const [field, value] of Object.entries(fields)) {
      if (value === null || value === undefined || value === "") {
        alert(`Please provide ${formatFieldName(field)}.`);
        return false;
      }
    }
    return true;
  };

  // ============================================================
  // FORMAT FIELD NAME
  // ============================================================

  const formatFieldName = (field) => {
    return field
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  // ============================================================
  // SAVE UPDATED PROFILE
  // ============================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);

      console.log("UPDATED PROFILE DATA:", formData);

      const result = await updateUserInfo(formData);

      console.log("UPDATE PROFILE RESPONSE:", result);

      if (result.status !== "success") {
        alert(result.error || "Failed to update profile.");
        return;
      }

      const latestUser = await getUserInfo();

      console.log("LATEST USER AFTER UPDATE:", latestUser);

      if (latestUser.status === "success" && latestUser.data) {
        localStorage.setItem("user", JSON.stringify(latestUser.data));
        window.dispatchEvent(new CustomEvent("userUpdated", { detail: latestUser.data }));
        console.log("USER UPDATED EVENT DISPATCHED");
      }

      alert("Profile updated successfully!");
      navigate("/recommendation-start");
    } catch (error) {
      console.error("UPDATE PROFILE ERROR:", error);
      alert(
        error.message ||
          "Something went wrong while updating your profile."
      );
    } finally {
      setSaving(false);
    }
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <h2>Loading your profile...</h2>
        <p>Please wait while we fetch your saved information.</p>
      </div>
    );
  }

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Update Your Profile</h1>
      <p style={styles.subtitle}>
        Change only the details you want to update.
      </p>

      <form onSubmit={handleSubmit}>
        {/* ====================================================
                            COMMON INFORMATION
        ==================================================== */}

        <div style={styles.section}>
          <h2 style={styles.sectionHeading}>Personal Information</h2>

          {/* AGE */}
          <Field label="Age">
            <input
              type="number"
              min="1"
              max="120"
              value={formData.age}
              onChange={(e) => updateField("age", e.target.value)}
              style={styles.input}
            />
          </Field>

          {/* GENDER */}
          <Field label="Gender">
            <select
              value={formData.gender}
              onChange={(e) => updateField("gender", e.target.value)}
              style={styles.input}
            >
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </Field>

          {/* STATE - Fixed to Maharashtra */}
          <Field label="State">
            <select
              value="Maharashtra"
              disabled
              style={styles.input}
            >
              <option value="Maharashtra">Maharashtra</option>
            </select>
            <p style={{ fontSize: "13px", color: "#666", marginTop: "8px" }}>
              Currently available only for Maharashtra
            </p>
          </Field>

          {/* DISTRICT */}
          <Field label="District">
            <select
              value={formData.district}
              onChange={(e) => updateField("district", e.target.value)}
              style={styles.input}
            >
              <option value="">Select district</option>
              {maharashtraDistricts.map((district) => (
                <option key={district} value={district}>
                  {district}
                </option>
              ))}
            </select>
          </Field>

          {/* MARITAL STATUS */}
          <Field label="Marital Status">
            <select
              value={formData.marital_status}
              onChange={(e) => updateField("marital_status", e.target.value)}
              style={styles.input}
            >
              <option value="">Select status</option>
              <option value="Single">Single</option>
              <option value="Married">Married</option>
              <option value="Widowed">Widowed</option>
              <option value="Divorced">Divorced</option>
              <option value="Separated">Separated</option>
            </select>
          </Field>

          {/* DISABILITY */}
          <Field label="Do you have any disability?">
            <YesNo
              value={formData.disability_status}
              onChange={(value) => updateField("disability_status", value)}
            />
          </Field>

          {/* INCOME */}
          <Field label="Annual Family Income">
            <input
              type="number"
              min="0"
              value={formData.annual_income}
              onChange={(e) => updateField("annual_income", e.target.value)}
              style={styles.input}
            />
          </Field>

          {/* BPL */}
          <Field label="Do you belong to a BPL household?">
            <YesNo
              value={formData.is_bpl}
              onChange={(value) => updateField("is_bpl", value)}
            />
          </Field>

          {/* AREA */}
          <Field label="Rural / Urban">
            <select
              value={formData.rural_urban}
              onChange={(e) => updateField("rural_urban", e.target.value)}
              style={styles.input}
            >
              <option value="">Select area</option>
              <option value="Rural">Rural</option>
              <option value="Urban">Urban</option>
            </select>
          </Field>

          {/* CASTE */}
          <Field label="Caste Category">
            <select
              value={formData.caste_category}
              onChange={(e) => updateField("caste_category", e.target.value)}
              style={styles.input}
            >
              <option value="">Select category</option>
              <option value="General">General</option>
              <option value="OBC">OBC</option>
              <option value="SC">SC</option>
              <option value="ST">ST</option>
              <option value="EWS">EWS</option>
            </select>
          </Field>

          {/* LOAN */}
          <Field label="Are you looking for a loan or financial assistance?">
            <YesNo
              value={formData.loan_required}
              onChange={(value) => updateField("loan_required", value)}
            />
          </Field>

          {/* HOUSE */}
          <Field label="Do you own a house?">
            <YesNo
              value={formData.house_ownership}
              onChange={(value) => updateField("house_ownership", value)}
            />
          </Field>

          {/* OCCUPATION */}
          <Field label="Current Occupation">
            <select
              value={formData.occupation}
              onChange={(e) => updateField("occupation", e.target.value)}
              style={styles.input}
            >
              <option value="">Select occupation</option>
              <option value="Student">Student</option>
              <option value="Farmer">Farmer</option>
              <option value="Business Owner / Self-employed">
                Business Owner / Self-employed
              </option>
              <option value="Homemaker">Homemaker</option>
              <option value="Other">Other</option>
            </select>
          </Field>
        </div>

        {/* ====================================================
                              STUDENT
        ==================================================== */}
        {formData.occupation === "Student" && (
          <div style={styles.section}>
            <h2 style={styles.sectionHeading}>Student Information</h2>

            <Field label="Education Level">
              <select
                value={formData.education_level}
                onChange={(e) => updateField("education_level", e.target.value)}
                style={styles.input}
              >
                <option value="">Select education level</option>
                {educationOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Course">
              <select
                value={formData.course}
                onChange={(e) => updateField("course", e.target.value)}
                style={styles.input}
              >
                <option value="">Select course</option>
                {courseOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Year / Standard of Study">
              <select
                value={formData.year_of_study}
                onChange={(e) => updateField("year_of_study", e.target.value)}
                style={styles.input}
              >
                <option value="">Select year / standard</option>
                {yearOfStudyOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Institution Type">
              <select
                value={formData.institution_type}
                onChange={(e) =>
                  updateField("institution_type", e.target.value)
                }
                style={styles.input}
              >
                <option value="">Select institution type</option>
                <option value="Government">Government</option>
                <option value="Private">Private</option>
                <option value="Aided">Aided</option>
              </select>
            </Field>

            <Field label="Are you receiving any scholarship?">
              <YesNo
                value={formData.current_scholarship}
                onChange={(value) =>
                  updateField("current_scholarship", value)
                }
              />
            </Field>
          </div>
        )}

        {/* ====================================================
                              FARMER
        ==================================================== */}
        {formData.occupation === "Farmer" && (
          <div style={styles.section}>
            <h2 style={styles.sectionHeading}>Farmer Information</h2>

            <Field label="Do you own agricultural land?">
              <YesNo
                value={formData.land_owner}
                onChange={(value) => updateField("land_owner", value)}
              />
            </Field>

            <Field label="Land Holding (in acres)">
              <input
                type="number"
                min="0"
                step="0.1"
                value={formData.land_holding}
                onChange={(e) => updateField("land_holding", e.target.value)}
                style={styles.input}
              />
            </Field>

            <Field label="Farming Type">
              <select
                value={formData.farming_type}
                onChange={(e) => updateField("farming_type", e.target.value)}
                style={styles.input}
              >
                <option value="">Select farming type</option>
                {farmingTypeOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Do you have access to irrigation?">
              <YesNo
                value={formData.irrigation_available}
                onChange={(value) =>
                  updateField("irrigation_available", value)
                }
              />
            </Field>

            <Field label="Do you have an agricultural loan?">
              <YesNo
                value={formData.agricultural_loan}
                onChange={(value) => updateField("agricultural_loan", value)}
              />
            </Field>
          </div>
        )}

        {/* ====================================================
                              BUSINESS
        ==================================================== */}
        {formData.occupation === "Business Owner / Self-employed" && (
          <div style={styles.section}>
            <h2 style={styles.sectionHeading}>Business Information</h2>

            <Field label="Business Type">
              <select
                value={formData.business_type}
                onChange={(e) => updateField("business_type", e.target.value)}
                style={styles.input}
              >
                <option value="">Select business type</option>
                {businessTypeOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Is your business registered?">
              <YesNo
                value={formData.business_registered}
                onChange={(value) =>
                  updateField("business_registered", value)
                }
              />
            </Field>

            <Field label="Business Age (Years)">
              <input
                type="number"
                min="0"
                value={formData.business_age}
                onChange={(e) => updateField("business_age", e.target.value)}
                style={styles.input}
              />
            </Field>

            <Field label="Annual Business Turnover">
              <input
                type="number"
                min="0"
                value={formData.business_turnover}
                onChange={(e) =>
                  updateField("business_turnover", e.target.value)
                }
                style={styles.input}
              />
            </Field>

            <Field label="Looking for business financial assistance?">
              <YesNo
                value={formData.business_financial_need}
                onChange={(value) =>
                  updateField("business_financial_need", value)
                }
              />
            </Field>
          </div>
        )}

        {/* ====================================================
                             HOMEMAKER
        ==================================================== */}
        {formData.occupation === "Homemaker" && (
          <div style={styles.section}>
            <h2 style={styles.sectionHeading}>Homemaker Information</h2>

            <Field label="Education Level">
              <select
                value={formData.education_level}
                onChange={(e) => updateField("education_level", e.target.value)}
                style={styles.input}
              >
                <option value="">Select education level</option>
                {educationOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Skills">
              <select
                value={formData.skills}
                onChange={(e) => updateField("skills", e.target.value)}
                style={styles.input}
              >
                <option value="">Select skill</option>
                {skillsOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Do you run a home-based business?">
              <YesNo
                value={formData.home_based_business}
                onChange={(value) =>
                  updateField("home_based_business", value)
                }
              />
            </Field>

            <Field label="Are you interested in starting a business?">
              <YesNo
                value={formData.business_interest}
                onChange={(value) => updateField("business_interest", value)}
              />
            </Field>
          </div>
        )}

        {/* ====================================================
                              BUTTONS
        ==================================================== */}
        <div style={styles.buttonContainer}>
          <button
            type="button"
            style={styles.cancelButton}
            onClick={() => navigate("/recommendation-start")}
            disabled={saving}
          >
            Cancel
          </button>

          <button
            type="submit"
            style={styles.saveButton}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

// ============================================================
// FIELD COMPONENT
// ============================================================

function Field({ label, children }) {
  return (
    <div style={styles.field}>
      <label style={styles.label}>{label}</label>
      {children}
    </div>
  );
}

// ============================================================
// YES / NO COMPONENT
// ============================================================

function YesNo({ value, onChange }) {
  return (
    <div style={styles.yesNoContainer}>
      <button
        type="button"
        style={{
          ...styles.optionButton,
          ...(value === true ? styles.selectedButton : {}),
        }}
        onClick={() => onChange(true)}
      >
        Yes
      </button>
      <button
        type="button"
        style={{
          ...styles.optionButton,
          ...(value === false ? styles.selectedButton : {}),
        }}
        onClick={() => onChange(false)}
      >
        No
      </button>
    </div>
  );
}

// ============================================================
// STYLES
// ============================================================

const styles = {
  loadingContainer: {
    maxWidth: "650px",
    margin: "100px auto",
    padding: "40px",
    textAlign: "center",
    fontFamily: "Arial",
  },
  container: {
    maxWidth: "700px",
    margin: "40px auto",
    padding: "35px",
    borderRadius: "12px",
    backgroundColor: "#ffffff",
    boxShadow: "0 0 15px rgba(0,0,0,0.1)",
    fontFamily: "Arial",
  },
  heading: {
    textAlign: "center",
    marginBottom: "10px",
  },
  subtitle: {
    textAlign: "center",
    color: "#666",
    marginBottom: "30px",
    lineHeight: "1.5",
  },
  section: {
    marginBottom: "30px",
    padding: "25px",
    borderRadius: "10px",
    backgroundColor: "#f9fafb",
  },
  sectionHeading: {
    marginTop: "0",
    marginBottom: "25px",
    color: "#1f2937",
  },
  field: {
    marginBottom: "20px",
  },
  label: {
    display: "block",
    marginBottom: "8px",
    fontWeight: "600",
    color: "#374151",
  },
  input: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "15px",
    boxSizing: "border-box",
    backgroundColor: "#fff",
  },
  yesNoContainer: {
    display: "flex",
    gap: "12px",
  },
  optionButton: {
    flex: 1,
    padding: "12px",
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
    gap: "15px",
    marginTop: "25px",
  },
  cancelButton: {
    flex: 1,
    padding: "13px",
    backgroundColor: "#6b7280",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
  },
  saveButton: {
    flex: 2,
    padding: "13px",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
  },
};

export default UpdateProfile;
