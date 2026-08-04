import { useState } from "react";

function FindSchemes() {

  const [step, setStep] = useState(1);

  const [formData, setFormData] = useState({
    gender: "",
    age: "",
    state: "",
    district: "",
    area: "",

    occupation: "",

    education_level: "",
    college_type: "",
    scholarship_needed: "",

    land_size: "",
    crop_type: "",
    irrigation: "",

    business_type: "",
    startup: "",
    annual_turnover: "",

    category: "",
    income: "",
    disability: "",
    minority: "",
    bpl: ""
  });

  const states = {
    Maharashtra: ["Pune", "Mumbai", "Nagpur"],
    Gujarat: ["Ahmedabad", "Surat"],
    Karnataka: ["Bangalore", "Mysore"],
    Delhi: ["New Delhi", "North Delhi"]
  };

  const progress = (step / 5) * 100;

  return (
    <div style={styles.container}>

      <h1 style={styles.heading}>
        Find Government Schemes
      </h1>

      {/* Progress Bar */}

      <div style={styles.progressContainer}>
        <div
          style={{
            ...styles.progressBar,
            width: `${progress}%`
          }}
        ></div>
      </div>



{step === 1 && (
  <div>

    <h2>Personal Details</h2>

    {/* Gender First */}

    <select
      value={formData.gender}
      onChange={(e) =>
        setFormData({
          ...formData,
          gender: e.target.value
        })
      }
      style={styles.input}
    >
      <option value="">Select Gender *</option>
      <option value="Male">Male</option>
      <option value="Female">Female</option>
      <option value="Other">Other</option>
    </select>

    {/* Age */}

    <input
      type="number"
      placeholder="Enter Age *"
      value={formData.age}
      onChange={(e) =>
        setFormData({
          ...formData,
          age: e.target.value
        })
      }
      style={styles.input}
    />

    {/* Category */}

    <select
      value={formData.category}
      onChange={(e) =>
        setFormData({
          ...formData,
          category: e.target.value
        })
      }
      style={styles.input}
    >
      <option value="">Select Category *</option>
      <option value="General">General</option>
      <option value="OBC">OBC</option>
      <option value="SC">SC</option>
      <option value="ST">ST</option>
    </select>

    <div style={styles.buttonContainer}>

      <button
        style={styles.nextButton}
        onClick={() => {

          if (
            formData.gender === "" ||
            formData.age === "" ||
            formData.category === ""
          ) {
            alert("Please fill all required fields");
            return;
          }

          setStep(2);
        }}
      >
        Next
      </button>

    </div>

  </div>
)}

{step === 2 && (
  <div>

    <h2>Location Details</h2>

    <select
      value={formData.state}
      onChange={(e) =>
        setFormData({
          ...formData,
          state: e.target.value,
          district: ""
        })
      }
      style={styles.input}
    >
      <option value="">Select State *</option>

      {Object.keys(states).map((state, index) => (
        <option key={index} value={state}>
          {state}
        </option>
      ))}

    </select>

    <select
      value={formData.district}
      onChange={(e) =>
        setFormData({
          ...formData,
          district: e.target.value
        })
      }
      style={styles.input}
    >
      <option value="">Select District *</option>

      {formData.state &&
        states[formData.state].map((district, index) => (
          <option key={index} value={district}>
            {district}
          </option>
        ))}

    </select>

    <select
      value={formData.area}
      onChange={(e) =>
        setFormData({
          ...formData,
          area: e.target.value
        })
      }
      style={styles.input}
    >
      <option value="">Select Area *</option>
      <option value="Urban">Urban</option>
      <option value="Rural">Rural</option>
    </select>

    <div style={styles.buttonContainer}>

      <button
        style={styles.backButton}
        onClick={() => setStep(1)}
      >
        Back
      </button>

      <button
        style={styles.nextButton}
        onClick={() => {

          if (
            formData.state === "" ||
            formData.district === "" ||
            formData.area === ""
          ) {
            alert("Please fill all required fields");
            return;
          }

          setStep(3);
        }}
      >
        Next
      </button>

    </div>

  </div>
)}



     

      {/* ================= STEP 3 ================= */}

      {step === 3 && (
        <div>

          <h2>Background Details</h2>

          <select
            value={formData.occupation}
            onChange={(e) =>
              setFormData({
                ...formData,
                occupation: e.target.value
              })
            }
            style={styles.input}
          >
            <option value="">Select Occupation</option>

            <option value="Student">
              Student
            </option>

            <option value="Farmer">
              Farmer
            </option>

            <option value="Business">
              Business Owner
            </option>

            <option value="Government Employee">
              Government Employee
            </option>

            <option value="Unemployed">
              Unemployed
            </option>

          </select>

          {/* ================= STUDENT QUESTIONS ================= */}

          {formData.occupation === "Student" && (
            <div>

              <select
                value={formData.education_level}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    education_level: e.target.value
                  })
                }
                style={styles.input}
              >
                <option value="">
                  Select Education Level
                </option>

                <option value="School">
                  School
                </option>

                <option value="Diploma">
                  Diploma
                </option>

                <option value="UG">
                  Undergraduate
                </option>

                <option value="PG">
                  Postgraduate
                </option>

              </select>

              <select
                value={formData.college_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    college_type: e.target.value
                  })
                }
                style={styles.input}
              >
                <option value="">
                  Select College Type
                </option>

                <option value="Government">
                  Government
                </option>

                <option value="Private">
                  Private
                </option>

              </select>

              <select
                value={formData.scholarship_needed}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    scholarship_needed: e.target.value
                  })
                }
                style={styles.input}
              >
                <option value="">
                  Scholarship Needed?
                </option>

                <option value="Yes">
                  Yes
                </option>

                <option value="No">
                  No
                </option>

              </select>

            </div>
          )}

          {/* ================= FARMER QUESTIONS ================= */}

          {formData.occupation === "Farmer" && (
            <div>

              <input
                type="text"
                placeholder="Enter Land Size"
                value={formData.land_size}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    land_size: e.target.value
                  })
                }
                style={styles.input}
              />

              <input
                type="text"
                placeholder="Enter Crop Type"
                value={formData.crop_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    crop_type: e.target.value
                  })
                }
                style={styles.input}
              />

              <select
                value={formData.irrigation}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    irrigation: e.target.value
                  })
                }
                style={styles.input}
              >
                <option value="">
                  Irrigation Available?
                </option>

                <option value="Yes">
                  Yes
                </option>

                <option value="No">
                  No
                </option>

              </select>

            </div>
          )}

          {/* ================= BUSINESS QUESTIONS ================= */}

          {formData.occupation === "Business" && (
            <div>

              <input
                type="text"
                placeholder="Enter Business Type"
                value={formData.business_type}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    business_type: e.target.value
                  })
                }
                style={styles.input}
              />

              <select
                value={formData.startup}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    startup: e.target.value
                  })
                }
                style={styles.input}
              >
                <option value="">
                  Is it Startup?
                </option>

                <option value="Yes">
                  Yes
                </option>

                <option value="No">
                  No
                </option>

              </select>

              <input
                type="number"
                placeholder="Annual Turnover"
                value={formData.annual_turnover}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    annual_turnover: e.target.value
                  })
                }
                style={styles.input}
              />

            </div>
          )}

          <div style={styles.buttonContainer}>

            <button
              style={styles.backButton}
              onClick={() => setStep(2)}
            >
              Back
            </button>

<button
  style={styles.nextButton}
  onClick={() => {

    if (formData.occupation === "") {
      alert("Please select occupation");
      return;
    }

    // Student Validation
    if (
      formData.occupation === "Student" &&
      (
        formData.education_level === "" ||
        formData.college_type === "" ||
        formData.scholarship_needed === ""
      )
    ) {
      alert("Please fill all student details");
      return;
    }

    // Farmer Validation
    if (
      formData.occupation === "Farmer" &&
      (
        formData.land_size === "" ||
        formData.crop_type === "" ||
        formData.irrigation === ""
      )
    ) {
      alert("Please fill all farmer details");
      return;
    }

    // Business Validation
    if (
      formData.occupation === "Business" &&
      (
        formData.business_type === "" ||
        formData.startup === "" ||
        formData.annual_turnover === ""
      )
    ) {
      alert("Please fill all business details");
      return;
    }

    setStep(4);

  }}
>
  Next
</button>



          </div>

        </div>
      )}

      {/* ================= STEP 4 ================= */}

      {step === 4 && (
        <div>

          <h2>Additional Details</h2>

          <input
            type="number"
            placeholder="Annual Family Income"
            value={formData.income}
            onChange={(e) =>
              setFormData({
                ...formData,
                income: e.target.value
              })
            }
            style={styles.input}
          />

          <select
            value={formData.disability}
            onChange={(e) =>
              setFormData({
                ...formData,
                disability: e.target.value
              })
            }
            style={styles.input}
          >
            <option value="">
              Any Disability?
            </option>

            <option value="Yes">
              Yes
            </option>

            <option value="No">
              No
            </option>

          </select>

          <select
            value={formData.minority}
            onChange={(e) =>
              setFormData({
                ...formData,
                minority: e.target.value
              })
            }
            style={styles.input}
          >
            <option value="">
              Minority Category?
            </option>

            <option value="Yes">
              Yes
            </option>

            <option value="No">
              No
            </option>

          </select>

          <select
            value={formData.bpl}
            onChange={(e) =>
              setFormData({
                ...formData,
                bpl: e.target.value
              })
            }
            style={styles.input}
          >
            <option value="">
              BPL Card Holder?
            </option>

            <option value="Yes">
              Yes
            </option>

            <option value="No">
              No
            </option>

          </select>

          <div style={styles.buttonContainer}>

            <button
              style={styles.backButton}
              onClick={() => setStep(3)}
            >
              Back
            </button>

<button
  style={styles.nextButton}
  onClick={() => {

    if (
      formData.income === "" ||
      formData.disability === "" ||
      formData.minority === "" ||
      formData.bpl === ""
    ) {
      alert("Please fill all required fields");
      return;
    }

    setStep(5);

  }}
>
  Next
</button>



          </div>

        </div>
      )}

      {/* ================= STEP 5 ================= */}

      {step === 5 && (
        <div>

          <h2>Review Details</h2>

          <div style={styles.reviewBox}>

            <p><strong>Gender:</strong> {formData.gender}</p>

            <p><strong>Category:</strong> {formData.category}</p>

            <p><strong>State:</strong> {formData.state}</p>

            <p><strong>District:</strong> {formData.district}</p>

            <p><strong>Area:</strong> {formData.area}</p>

            <p><strong>Occupation:</strong> {formData.occupation}</p>

            <p><strong>Income:</strong> ₹{formData.income}</p>

          </div>

          <div style={styles.buttonContainer}>

            <button
              style={styles.backButton}
              onClick={() => setStep(4)}
            >
              Back
            </button>

            <button style={styles.nextButton}>
              Find Eligible Schemes
            </button>

          </div>

        </div>
      )}

    </div>
  );
}

/* ================= STYLES ================= */

const styles = {

  container: {
    maxWidth: "750px",
    margin: "40px auto",
    padding: "30px",
    borderRadius: "12px",
    backgroundColor: "#ffffff",
    boxShadow: "0 0 15px rgba(0,0,0,0.1)",
    fontFamily: "Arial"
  },

  heading: {
    textAlign: "center",
    color: "#2563eb",
    marginBottom: "20px"
  },

  input: {
    width: "100%",
    padding: "12px",
    marginTop: "15px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "15px"
  },

  progressContainer: {
    width: "100%",
    height: "10px",
    backgroundColor: "#e5e7eb",
    borderRadius: "10px",
    marginBottom: "30px"
  },

  progressBar: {
    height: "100%",
    backgroundColor: "#2563eb",
    borderRadius: "10px"
  },

  buttonContainer: {
    marginTop: "25px"
  },

  nextButton: {
    padding: "12px 20px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    marginRight: "10px"
  },

  backButton: {
    padding: "12px 20px",
    backgroundColor: "#6b7280",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer"
  },

  reviewBox: {
    backgroundColor: "#f9fafb",
    padding: "20px",
    borderRadius: "10px",
    marginTop: "20px"
  }

};

export default FindSchemes;