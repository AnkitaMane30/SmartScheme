import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getRecommendations } from "../services/userServices";
import { toast } from "react-toastify";

function Recommendations() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);

        const token = localStorage.getItem("token");
        if (!token) {
          toast.error("Please login first");
          navigate("/login");
          return;
        }

        const result = await getRecommendations();

        if (result?.status === "success") {
          setData(result.data);
        } else {
          throw new Error(result?.error || "Failed to load recommendations");
        }
      } catch (err) {
        console.error("RECOMMENDATIONS ERROR:", err);
        setError(err.message || "Something went wrong");
        toast.error(err.message || "Failed to load recommendations");
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [navigate]);

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------
  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.heading}>Finding best schemes for you...</h2>
          <p style={styles.subText}>
            Analyzing your profile with eligibility rules + AI ranking.
          </p>
          <div style={styles.spinner}></div>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // ERROR
  // --------------------------------------------------
  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={{ ...styles.heading, color: "#dc2626" }}>
            Unable to load recommendations
          </h2>
          <p style={styles.subText}>{error}</p>
          <div style={styles.buttonRow}>
            <button style={styles.primaryBtn} onClick={() => navigate("/update-profile")}>
              Update Profile
            </button>
            <button style={styles.secondaryBtn} onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const recommendations = data?.recommendations || [];

  // --------------------------------------------------
  // MAIN UI
  // --------------------------------------------------
  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>Your Personalized Recommendations</h1>
        <p style={styles.subtitle}>
          Based on your profile • Ranked by eligibility + relevance
        </p>

        <div style={styles.statsRow}>
          <div style={styles.statBox}>
            <div style={styles.statNumber}>{data?.eligible_count ?? 0}</div>
            <div style={styles.statLabel}>Eligible</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statNumber}>{data?.needs_verification_count ?? 0}</div>
            <div style={styles.statLabel}>Needs Verification</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statNumber}>{data?.not_eligible_count ?? 0}</div>
            <div style={styles.statLabel}>Not Eligible</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statNumber}>{data?.total_schemes ?? 0}</div>
            <div style={styles.statLabel}>Total Schemes</div>
          </div>
        </div>
      </div>

      {recommendations.length === 0 ? (
        <div style={styles.emptyCard}>
          <h3>No matching schemes found</h3>
          <p>Try updating your profile with more accurate details.</p>
          <button style={styles.primaryBtn} onClick={() => navigate("/update-profile")}>
            Update Profile
          </button>
        </div>
      ) : (
        <div style={styles.list}>
          {recommendations.map((item, index) => (
            <div key={item.scheme_id || index} style={styles.cardItem}>
              <div style={styles.rankBadge}>#{index + 1}</div>

              <div style={styles.cardContent}>
                <h3 style={styles.schemeTitle}>{item.scheme_name}</h3>

                <div style={styles.metaRow}>
                  <span style={styles.badge}>{item.category || "General"}</span>
                  {item.department && (
                    <span style={styles.dept}>{item.department}</span>
                  )}
                </div>

                <div style={styles.scoreRow}>
                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>Final Score</span>
                    <span style={styles.scoreValue}>{item.final_score}</span>
                  </div>
                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>TF-IDF</span>
                    <span style={styles.scoreValue}>{item.tfidf_score}</span>
                  </div>
                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>ML</span>
                    <span style={styles.scoreValue}>{item.ml_score}</span>
                  </div>
                  <div style={styles.scoreItem}>
                    <span style={styles.scoreLabel}>Boost</span>
                    <span style={styles.scoreValue}>+{item.category_boost}</span>
                  </div>
                </div>

                <div style={styles.actions}>
                  {item.url ? (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.applyBtn}
                    >
                      Apply / Visit Official Site
                    </a>
                  ) : (
                    <span style={styles.noLink}>No official link available</span>
                  )}

                  <Link
                    to={`/schemes/${item.scheme_id}`}
                    style={styles.detailsBtn}
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={styles.footerActions}>
        <button style={styles.secondaryBtn} onClick={() => navigate("/update-profile")}>
          Update Profile
        </button>
        <button style={styles.secondaryBtn} onClick={() => navigate("/schemes")}>
          Browse All Schemes
        </button>
      </div>
    </div>
  );
}

// ============================================================
// STYLES
// ============================================================

const styles = {
  page: {
    maxWidth: "900px",
    margin: "40px auto",
    padding: "0 20px 60px",
    fontFamily: "Arial, sans-serif",
  },
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "70vh",
    padding: "20px",
  },
  card: {
    background: "#fff",
    padding: "40px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
    textAlign: "center",
    maxWidth: "480px",
    width: "100%",
  },
  heading: {
    margin: "0 0 12px",
    color: "#1f2937",
  },
  subText: {
    color: "#6b7280",
    marginBottom: "24px",
  },
  spinner: {
    width: "40px",
    height: "40px",
    border: "4px solid #e5e7eb",
    borderTop: "4px solid #2563eb",
    borderRadius: "50%",
    margin: "0 auto",
    animation: "spin 0.8s linear infinite",
  },
  header: {
    textAlign: "center",
    marginBottom: "32px",
  },
  title: {
    fontSize: "28px",
    color: "#111827",
    marginBottom: "8px",
  },
  subtitle: {
    color: "#6b7280",
    marginBottom: "24px",
  },
  statsRow: {
    display: "flex",
    justifyContent: "center",
    gap: "16px",
    flexWrap: "wrap",
  },
  statBox: {
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "12px",
    padding: "14px 20px",
    minWidth: "110px",
  },
  statNumber: {
    fontSize: "22px",
    fontWeight: "700",
    color: "#1e40af",
  },
  statLabel: {
    fontSize: "13px",
    color: "#64748b",
    marginTop: "4px",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "18px",
  },
  cardItem: {
    display: "flex",
    gap: "16px",
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: "14px",
    padding: "20px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.04)",
    transition: "transform 0.15s ease",
  },
  rankBadge: {
    flexShrink: 0,
    width: "42px",
    height: "42px",
    borderRadius: "50%",
    background: "#2563eb",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "700",
    fontSize: "16px",
  },
  cardContent: {
    flex: 1,
  },
  schemeTitle: {
    margin: "0 0 10px",
    fontSize: "18px",
    color: "#111827",
    lineHeight: 1.3,
  },
  metaRow: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "12px",
    flexWrap: "wrap",
  },
  badge: {
    background: "#dbeafe",
    color: "#1e40af",
    fontSize: "12px",
    fontWeight: "600",
    padding: "4px 10px",
    borderRadius: "20px",
  },
  dept: {
    fontSize: "13px",
    color: "#6b7280",
  },
  scoreRow: {
    display: "flex",
    gap: "18px",
    marginBottom: "16px",
    flexWrap: "wrap",
  },
  scoreItem: {
    display: "flex",
    flexDirection: "column",
  },
  scoreLabel: {
    fontSize: "11px",
    color: "#9ca3af",
    textTransform: "uppercase",
    letterSpacing: "0.4px",
  },
  scoreValue: {
    fontSize: "15px",
    fontWeight: "600",
    color: "#374151",
  },
  actions: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
    alignItems: "center",
  },
  applyBtn: {
    background: "#16a34a",
    color: "#fff",
    padding: "9px 16px",
    borderRadius: "8px",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: "600",
  },
  detailsBtn: {
    background: "#f3f4f6",
    color: "#374151",
    padding: "9px 16px",
    borderRadius: "8px",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: "500",
  },
  noLink: {
    fontSize: "13px",
    color: "#9ca3af",
  },
  emptyCard: {
    textAlign: "center",
    background: "#fff",
    padding: "50px 30px",
    borderRadius: "14px",
    border: "1px dashed #d1d5db",
  },
  footerActions: {
    display: "flex",
    justifyContent: "center",
    gap: "14px",
    marginTop: "40px",
    flexWrap: "wrap",
  },
  primaryBtn: {
    background: "#2563eb",
    color: "#fff",
    border: "none",
    padding: "12px 22px",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "15px",
    fontWeight: "600",
  },
  secondaryBtn: {
    background: "#f3f4f6",
    color: "#374151",
    border: "1px solid #d1d5db",
    padding: "12px 22px",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "15px",
  },
  buttonRow: {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    flexWrap: "wrap",
  },
};

export default Recommendations;