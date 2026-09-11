import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getSchemeById } from "../services/schemeService";

export default function SchemeDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);

  // =====================================================
  // LOAD SCHEME
  // =====================================================

  useEffect(() => {
    loadScheme();
  }, [id]);

  const loadScheme = async () => {
    try {
      setLoading(true);
      const result = await getSchemeById(id);
      console.log("SCHEME DATA:", result);
      setScheme(result);
    } catch (error) {
      console.error("Error loading scheme:", error);
      setScheme(null);
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // HELPER FUNCTIONS
  // =====================================================

  const hasValue = (value) => {
    if (value === null || value === undefined) return false;
    const text = value.toString().trim();
    return (
      text !== "" &&
      text.toLowerCase() !== "not available" &&
      text.toLowerCase() !== "na" &&
      text.toLowerCase() !== "n/a" &&
      text.toLowerCase() !== "null" &&
      text.toLowerCase() !== "undefined"
    );
  };

  const cleanScrapedText = (value) => {
    if (!hasValue(value)) return "";

    let text = value.toString();

    // Normalize line breaks
    text = text.replace(/\r\n/g, "\n");
    text = text.replace(/\r/g, "\n");

    // Remove excessive spaces
    text = text.replace(/[ \t]+/g, " ");

    // Keep exactly one blank line between paragraphs
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
  };

  const removeDuplicateContent = (value) => {
    const text = cleanScrapedText(value);
    if (!text) return [];

    let blocks = text
      .split(/\n\s*\n/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    if (blocks.length === 1 && blocks[0].includes("\n")) {
      blocks = blocks[0]
        .split("\n")
        .map((item) => item.trim())
        .filter((item) => item.length > 0);
    }

    const uniqueBlocks = [];
    const seen = new Set();

    blocks.forEach((block) => {
      const normalized = block
        .toLowerCase()
        .replace(/\s+/g, " ")
        .replace(/[•●▪]/g, "")
        .trim();

      if (!normalized) return;

      if (!seen.has(normalized)) {
        seen.add(normalized);
        uniqueBlocks.push(block);
      }
    });

    return uniqueBlocks;
  };

  const renderScrapedContent = (value) => {
    if (!hasValue(value)) return null;

    const contentBlocks = removeDuplicateContent(value);

    return (
      <div className="scheme-details-text">
        {contentBlocks.map((block, index) => {
          const lines = block
            .split("\n")
            .map((line) => line.trim())
            .filter((line) => line.length > 0);

          return (
            <div key={index} className="scheme-content-block">
              {lines.map((line, lineIndex) => (
                <p key={lineIndex} className="scheme-content-line">
                  {line}
                </p>
              ))}
            </div>
          );
        })}
      </div>
    );
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="container py-5 text-center">
        <div className="spinner-border text-primary"></div>
        <p className="mt-3">Loading scheme details...</p>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="container py-5 text-center">
        <h3 className="text-danger">Scheme Not Found</h3>
        <p className="mt-3">The scheme you are looking for does not exist.</p>
        <button
          className="btn btn-primary mt-4"
          onClick={() => navigate("/schemes")}
        >
          Back to Schemes
        </button>
      </div>
    );
  }

  // =====================================================
  // MAIN UI - PROFESSIONAL DOCUMENT STYLE
  // =====================================================

  return (
    <div className="container py-5">
      <button
        className="btn btn-link text-decoration-none mb-4"
        onClick={() => navigate("/schemes")}
      >
        ← Back to Schemes
      </button>

      <div className="row">
        {/* LEFT MENU (Navigation) */}
        <div className="col-md-3">
          <div
            className="card border-0 shadow-sm sticky-top"
            style={{ top: "20px", maxHeight: "90vh", overflowY: "auto" }}
          >
            <div className="list-group list-group-flush">
              <a href="#details" className="list-group-item list-group-item-action">
                Details
              </a>
              {hasValue(scheme.benefits) && (
                <a href="#benefits" className="list-group-item list-group-item-action">
                  Benefits
                </a>
              )}
              {hasValue(scheme.eligibility) && (
                <a href="#eligibility" className="list-group-item list-group-item-action">
                  Eligibility
                </a>
              )}
              {hasValue(scheme.exclusion) && (
                <a href="#exclusion" className="list-group-item list-group-item-action">
                  Exclusions
                </a>
              )}
              {hasValue(scheme.documents_required) && (
                <a href="#documents" className="list-group-item list-group-item-action">
                  Documents Required
                </a>
              )}
              {hasValue(scheme.application_process) && (
                <a href="#process" className="list-group-item list-group-item-action">
                  Application Process
                </a>
              )}
              {(hasValue(scheme.min_age) ||
                hasValue(scheme.max_age) ||
                hasValue(scheme.gender) ||
                hasValue(scheme.target_group) ||
                hasValue(scheme.min_income) ||
                hasValue(scheme.max_income)) && (
                <a href="#additional" className="list-group-item list-group-item-action">
                  Additional Information
                </a>
              )}
            </div>
          </div>
        </div>

        {/* MAIN CONTENT */}
        <div className="col-md-9">
          <div className="card border-0 shadow-sm p-4">

            {/* Header */}
            {hasValue(scheme.department) && (
              <p className="text-muted mb-2 scheme-department">{scheme.department}</p>
            )}
            <h1 className="fw-bold mb-3 scheme-title">{scheme.title}</h1>

            {/* Tags */}
            <div className="mb-4">
              {hasValue(scheme.category) && (
                <span className="badge bg-success me-2">{scheme.category}</span>
              )}
              {hasValue(scheme.state) && (
                <span className="badge bg-primary me-2">{scheme.state}</span>
              )}
              {hasValue(scheme.status) && (
                <span className="badge bg-warning text-dark">{scheme.status}</span>
              )}
            </div>

            {/* Action Buttons */}
            <div className="mb-4">
              <button
                className="btn btn-outline-primary me-3"
                onClick={() => document.getElementById("eligibility")?.scrollIntoView({ behavior: "smooth" })}
              >
                Check Eligibility
              </button>
              {hasValue(scheme.application_link) && (
                <a
                  href={scheme.application_link}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-primary"
                >
                  Apply Now
                </a>
              )}
            </div>

            <hr className="my-4" />

            {/* DETAILS */}
            {hasValue(scheme.details) && (
              <section id="details" className="scheme-section">
                <h3 className="scheme-section-title">Details</h3>
                {renderScrapedContent(scheme.details)}
              </section>
            )}

            {/* BENEFITS */}
            {hasValue(scheme.benefits) && (
              <section id="benefits" className="scheme-section">
                <h3 className="scheme-section-title">Benefits</h3>
                {renderScrapedContent(scheme.benefits)}
              </section>
            )}

            {/* ELIGIBILITY */}
            {hasValue(scheme.eligibility) && (
              <section id="eligibility" className="scheme-section">
                <h3 className="scheme-section-title">Eligibility</h3>
                {renderScrapedContent(scheme.eligibility)}
              </section>
            )}

            {/* EXCLUSIONS */}
            {hasValue(scheme.exclusion) && (
              <section id="exclusion" className="scheme-section">
                <h3 className="scheme-section-title">Exclusions</h3>
                {renderScrapedContent(scheme.exclusion)}
              </section>
            )}

            {/* DOCUMENTS REQUIRED */}
            {hasValue(scheme.documents_required) && (
              <section id="documents" className="scheme-section">
                <h3 className="scheme-section-title">Documents Required</h3>
                {renderScrapedContent(scheme.documents_required)}
              </section>
            )}

            {/* APPLICATION PROCESS */}
            {hasValue(scheme.application_process) && (
              <section id="process" className="scheme-section">
                <h3 className="scheme-section-title">Application Process</h3>
                {renderScrapedContent(scheme.application_process)}
              </section>
            )}

            {/* ADDITIONAL INFORMATION */}
            {(hasValue(scheme.min_age) ||
              hasValue(scheme.max_age) ||
              hasValue(scheme.gender) ||
              hasValue(scheme.target_group) ||
              hasValue(scheme.min_income) ||
              hasValue(scheme.max_income)) && (
              <section id="additional" className="scheme-section">
                <h3 className="scheme-section-title">Additional Information</h3>

                <div className="row g-3">
                  {hasValue(scheme.min_age) && (
                    <div className="col-md-6">
                      <div className="additional-info-card">
                        <strong>Minimum Age</strong>
                        <div className="mt-1">{scheme.min_age}</div>
                      </div>
                    </div>
                  )}
                  {hasValue(scheme.max_age) && (
                    <div className="col-md-6">
                      <div className="additional-info-card">
                        <strong>Maximum Age</strong>
                        <div className="mt-1">{scheme.max_age}</div>
                      </div>
                    </div>
                  )}
                  <div className="col-md-6">
                    <div className="additional-info-card">
                      <strong>Gender</strong>
                      <div className="mt-1">{scheme.gender || "All"}</div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="additional-info-card">
                      <strong>Target Group</strong>
                      <div className="mt-1">{scheme.target_group || "Citizens"}</div>
                    </div>
                  </div>
                  {hasValue(scheme.min_income) && (
                    <div className="col-md-6">
                      <div className="additional-info-card">
                        <strong>Minimum Income</strong>
                        <div className="mt-1">₹ {scheme.min_income}</div>
                      </div>
                    </div>
                  )}
                  {hasValue(scheme.max_income) && (
                    <div className="col-md-6">
                      <div className="additional-info-card">
                        <strong>Maximum Income</strong>
                        <div className="mt-1">₹ {scheme.max_income}</div>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
