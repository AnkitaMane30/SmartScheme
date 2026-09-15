import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getProfileStatus } from "../services/userServices";

function RecommendationStart() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [profileCompleted, setProfileCompleted] = useState(false);

  // ============================================================
  // CHECK PROFILE STATUS
  // ============================================================

  const checkProfile = async () => {
    try {
      setLoading(true);

      const result = await getProfileStatus();

      console.log("PROFILE STATUS:", result);

      if (result?.status !== "success") {
        console.error(
          "PROFILE STATUS RESPONSE ERROR:",
          result
        );

        setProfileCompleted(false);
        return;
      }

      // ========================================================
      // HANDLE BOOLEAN / INTEGER / STRING VALUES
      // Backend may return:
      // true
      // 1
      // "1"
      // ========================================================

      const profileCompletedValue =
        result.data?.profile_completed;

      const isCompleted =
        profileCompletedValue === true ||
        profileCompletedValue === 1 ||
        profileCompletedValue === "1";

      console.log(
        "PROFILE COMPLETED VALUE:",
        profileCompletedValue
      );

      console.log(
        "PROFILE COMPLETED:",
        isCompleted
      );

      setProfileCompleted(isCompleted);

    } catch (error) {

      console.error(
        "PROFILE STATUS ERROR:",
        error
      );

      alert(
        error.message ||
        "Unable to check your profile."
      );

    } finally {

      setLoading(false);

    }
  };

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {

    checkProfile();

  }, []);

  // ============================================================
  // LISTEN FOR PROFILE UPDATE
  // ============================================================
  //
  // If UpdateProfile changes the user's profile, it dispatches:
  //
  // window.dispatchEvent(
  //   new CustomEvent("userUpdated", {
  //     detail: updatedUser
  //   })
  // );
  //
  // We check the profile status again so this page always
  // displays the latest backend state.
  // ============================================================

  useEffect(() => {

    const handleUserUpdated = () => {

      console.log(
        "USER UPDATED EVENT RECEIVED BY RECOMMENDATION START"
      );

      checkProfile();

    };

    window.addEventListener(
      "userUpdated",
      handleUserUpdated
    );

    return () => {

      window.removeEventListener(
        "userUpdated",
        handleUserUpdated
      );

    };

  }, []);

  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {

    return (
      <div style={styles.container}>

        <h2 style={styles.loadingHeading}>
          Checking your profile...
        </h2>

        <p style={styles.text}>
          Please wait while we check your profile status.
        </p>

      </div>
    );
  }

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div style={styles.container}>

      <h1 style={styles.heading}>
        Find Government Schemes
      </h1>

      {!profileCompleted ? (

        <>
          <p style={styles.text}>
            Complete your profile once to find government
            schemes based on your eligibility.
          </p>

          <button
            style={styles.button}
            onClick={() =>
              navigate("/findscheme")
            }
          >
            Complete Profile
          </button>
        </>

      ) : (

        <>
          <p style={styles.successText}>
            Your profile is already completed.
          </p>

          <p style={styles.text}>
            You can update your details or view your
            personalized government scheme recommendations.
          </p>

          <div style={styles.buttonContainer}>

            <button
              style={styles.button}
              onClick={() =>
                navigate("/update-profile")
              }
            >
              Update Profile
            </button>

            <button
              style={styles.secondaryButton}
              onClick={() =>
                navigate("/recommendations")
              }
            >
              View Recommendations
            </button>

          </div>
        </>

      )}

    </div>
  );
}

// ============================================================
// STYLES
// ============================================================

const styles = {

  container: {
    maxWidth: "650px",
    margin: "80px auto",
    padding: "40px",
    textAlign: "center",
    backgroundColor: "#ffffff",
    borderRadius: "12px",
    boxShadow: "0 0 15px rgba(0,0,0,0.1)",
    fontFamily: "Arial, sans-serif"
  },

  heading: {
    marginBottom: "20px",
    color: "#1f2937"
  },

  loadingHeading: {
    color: "#1f2937",
    marginBottom: "15px"
  },

  text: {
    color: "#666",
    marginBottom: "30px",
    lineHeight: "1.6"
  },

  successText: {
    color: "#16a34a",
    fontWeight: "600",
    marginBottom: "15px"
  },

  buttonContainer: {
    display: "flex",
    justifyContent: "center",
    gap: "12px",
    flexWrap: "wrap"
  },

  button: {
    padding: "13px 25px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
    margin: "5px"
  },

  secondaryButton: {
    padding: "13px 25px",
    backgroundColor: "#6b7280",
    color: "#ffffff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "16px",
    margin: "5px"
  }

};

export default RecommendationStart;