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

    text = text.replace(/\r\n/g, "\n");
    text = text.replace(/\r/g, "\n");
    text = text.replace(/[ \t]+/g, " ");
    text = text.replace(/\n{3,}/g, "\n\n");

    return text.trim();
  };

  // ---------------------------------------------------------------
  // Date extraction (used for the duration badge next to the title)
  // ---------------------------------------------------------------
  const DATE_LINE_REGEX = /Date\s*:\s*(\d{2})\/(\d{2})\/(\d{4})\s*-\s*(?:(\d{2})\/(\d{2})\/(\d{4}))?/;
  const GLOBAL_DATE_REGEX = /Date\s*:\s*\d{2}\/\d{2}\/\d{4}\s*-\s*(?:\d{2}\/\d{2}\/\d{4})?/g;

  const parseDDMMYYYY = (dd, mm, yyyy) => {
    if (!dd || !mm || !yyyy) return null;
    const date = new Date(Number(yyyy), Number(mm) - 1, Number(dd));
    return isNaN(date.getTime()) ? null : date;
  };

  const extractDateRange = (rawText) => {
    if (!hasValue(rawText)) {
      return { startDate: null, endDate: null, cleanedText: rawText };
    }

    const text = rawText.toString();
    const match = text.match(DATE_LINE_REGEX);

    if (!match) {
      return { startDate: null, endDate: null, cleanedText: text };
    }

    const [fullMatch, sd, sm, sy, ed, em, ey] = match;
    const startDate = parseDDMMYYYY(sd, sm, sy);
    const endDate = ed ? parseDDMMYYYY(ed, em, ey) : null;

    const cleanedText = text.replace(fullMatch, "").trim();

    return { startDate, endDate, cleanedText };
  };

  const formatDate = (date) => {
    if (!date) return null;
    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  // Strip every "Date : dd/mm/yyyy - dd/mm/yyyy" occurrence out of a
  // block of text (there can be more than one when the scraper picked
  // up a repeated chunk that each carried its own date line).
  const stripEmbeddedDates = (text) =>
    text.replace(GLOBAL_DATE_REGEX, " ").replace(/\s{2,}/g, " ").trim();

  // ---------------------------------------------------------------
  // Generic de-duplication used at TWO levels:
  //   1. block level  - separate paragraphs split by blank lines
  //   2. sentence level - inside one oversized run-on block that has
  //      no line breaks at all, where the same passage was scraped
  //      twice back-to-back (often with a stray "Date:" in between)
  // Removes exact repeats AND repeats that are a shorter substring of
  // a longer, otherwise-identical passage.
  // ---------------------------------------------------------------
  const normalizeForCompare = (text) =>
    text
      .toLowerCase()
      .replace(/[•●▪]/g, "")
      .replace(/\s+/g, " ")
      .trim();

  const dedupeStrings = (items) => {
    const uniqueItems = [];
    const seenNormalized = [];

    items.forEach((item) => {
      const normalized = normalizeForCompare(item);
      if (!normalized) return;

      if (seenNormalized.includes(normalized)) return;

      const isSubsetOfKept = seenNormalized.some(
        (kept) => kept.includes(normalized) && kept !== normalized
      );
      if (isSubsetOfKept) return;

      for (let i = uniqueItems.length - 1; i >= 0; i--) {
        if (normalized.includes(seenNormalized[i]) && normalized !== seenNormalized[i]) {
          uniqueItems.splice(i, 1);
          seenNormalized.splice(i, 1);
        }
      }

      uniqueItems.push(item);
      seenNormalized.push(normalized);
    });

    return uniqueItems;
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

    return dedupeStrings(blocks);
  };

  // Split a run-on passage into sentences for sentence-level dedupe.
  const splitIntoSentences = (text) => {
    const matches = text.match(/[^.!?]+[.!?]+(?=\s|$)/g);
    if (matches && matches.length > 1) {
      return matches.map((s) => s.trim()).filter(Boolean);
    }
    return [text.trim()].filter(Boolean);
  };

  // ---------------------------------------------------------------
  // MEANINGFUL CONTENT RENDERING
  //
  //   heading   - short Title-Case line, no period/comma  -> <h5>
  //   table     - pipe-separated data row                  -> <table>
  //   labelled  - "Label: description" line                -> bold-label bullet
  //   bullet    - a short-to-medium standalone sentence     -> plain bullet
  //   paragraph - a single, moderate-length sentence/line   -> <p>
  //   narrative - an oversized run-on block with no line
  //               breaks at all (often internally duplicated) ->
  //               de-duplicated at the SENTENCE level, then
  //               regrouped into a few readable <p> paragraphs
  // ---------------------------------------------------------------

  const isTableRow = (line) =>
    line.split("|").map((p) => p.trim()).filter(Boolean).length >= 3;

  const LABEL_LINE_REGEX = /^([A-Za-z][A-Za-z0-9()/&,'.\-\s]{2,70}?):\s+(.+)$/;

  const isLikelyHeading = (line) => {
    if (line.length > 70) return false;
    if (line.endsWith(".") || line.includes(",") || line.includes(":")) return false;
    if (/\d/.test(line)) return false;
    const words = line.split(/\s+/).filter(Boolean);
    if (words.length > 8) return false;
    const capitalizedCount = words.filter((w) => /^[A-Z]/.test(w)).length;
    return capitalizedCount >= Math.ceil(words.length * 0.6);
  };

  const NARRATIVE_THRESHOLD = 400;
  const SENTENCES_PER_PARAGRAPH = 3;

  const buildNarrativeGroup = (block) => {
    const stripped = stripEmbeddedDates(block);
    const sentences = splitIntoSentences(stripped);
    const uniqueSentences = dedupeStrings(sentences);

    const paragraphs = [];
    for (let i = 0; i < uniqueSentences.length; i += SENTENCES_PER_PARAGRAPH) {
      paragraphs.push(uniqueSentences.slice(i, i + SENTENCES_PER_PARAGRAPH).join(" "));
    }

    return { type: "narrative", lines: paragraphs.length ? paragraphs : [stripped] };
  };

  const classifyBlock = (block) => {
    const lines = block
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    if (lines.length > 1) {
      return { type: "complex", lines };
    }

    const line = lines[0] || "";

    // A single, very long line with no internal breaks is often a
    // scraper artifact where the same passage got captured twice -
    // run it through sentence-level dedupe instead of printing it
    // as one giant unbroken paragraph.
    if (line.length > NARRATIVE_THRESHOLD) {
      return buildNarrativeGroup(line);
    }

    if (isTableRow(line)) return { type: "table", line };
    if (isLikelyHeading(line)) return { type: "heading", line };
    if (LABEL_LINE_REGEX.test(line)) return { type: "labelled", line };
    if (line.length <= 300) return { type: "bullet", line };
    return { type: "paragraph", line };
  };

  // Group consecutive blocks of the same renderable type together so
  // they render as ONE list / ONE table instead of many separately
  // spaced paragraphs.
  const groupBlocks = (blocks) => {
    const classified = blocks.map(classifyBlock);
    const groups = [];
    let current = null;

    classified.forEach((item) => {
      // "complex" and "narrative" blocks are already fully resolved
      // and always stand alone - never merged with neighbours.
      if (item.type === "complex" || item.type === "narrative") {
        if (current) groups.push(current);
        current = null;
        groups.push(item);
        return;
      }

      const mergeable = item.type === "table" || item.type === "labelled" || item.type === "bullet";

      if (mergeable && current && current.type === item.type) {
        current.lines.push(item.line);
      } else {
        if (current) groups.push(current);
        current = { type: item.type, lines: [item.line] };
        if (!mergeable) {
          groups.push(current);
          current = null;
        }
      }
    });
    if (current) groups.push(current);

    return groups;
  };

  const renderComplexBlock = (lines, key) => {
    const rows = [];
    let bulletBuffer = [];

    const flushBullets = () => {
      if (bulletBuffer.length) {
        rows.push(
          <ul className="scheme-bullet-list" key={`b-${rows.length}`}>
            {bulletBuffer.map((l, i) => (
              <li key={i}>{l.replace(/^[•●▪\-*]\s*/, "")}</li>
            ))}
          </ul>
        );
        bulletBuffer = [];
      }
    };

    lines.forEach((line, idx) => {
      if (isTableRow(line)) {
        flushBullets();
        rows.push(
          <div className="table-responsive scheme-table-wrap" key={`t-${idx}`}>
            <table className="table table-sm table-bordered scheme-data-table">
              <tbody>
                <tr>
                  {line.split("|").map((cell, cIdx) => (
                    <td key={cIdx}>{cell.trim()}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        );
      } else if (line.length <= 300 && !isLikelyHeading(line)) {
        bulletBuffer.push(line);
      } else {
        flushBullets();
        rows.push(
          <p className="scheme-content-line" key={`p-${idx}`}>
            {line}
          </p>
        );
      }
    });
    flushBullets();

    return (
      <div className="scheme-content-block" key={key}>
        {rows}
      </div>
    );
  };

  const renderGroup = (group, index) => {
    if (group.type === "complex") {
      return renderComplexBlock(group.lines, index);
    }

    if (group.type === "narrative") {
      return (
        <div className="scheme-content-block" key={index}>
          {group.lines.map((paragraph, pIdx) => (
            <p className="scheme-content-line scheme-paragraph" key={pIdx}>
              {paragraph}
            </p>
          ))}
        </div>
      );
    }

    if (group.type === "heading") {
      return (
        <h5 className="scheme-subheading" key={index}>
          {group.lines[0]}
        </h5>
      );
    }

    if (group.type === "table") {
      const rows = group.lines.map((line) =>
        line.split("|").map((cell) => cell.trim()).filter((cell) => cell.length > 0)
      );
      const colCount = Math.max(...rows.map((r) => r.length));

      return (
        <div className="table-responsive scheme-table-wrap" key={index}>
          <table className="table table-sm table-bordered scheme-data-table">
            <tbody>
              {rows.map((row, rIdx) => (
                <tr key={rIdx}>
                  {Array.from({ length: colCount }).map((_, cIdx) => (
                    <td key={cIdx}>{row[cIdx] || ""}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (group.type === "labelled") {
      return (
        <ul className="scheme-label-list" key={index}>
          {group.lines.map((line, lIdx) => {
            const match = line.match(LABEL_LINE_REGEX);
            const label = match ? match[1].trim() : "";
            const description = match ? match[2].trim() : line;
            return (
              <li className="scheme-label-item" key={lIdx}>
                <span className="scheme-label-text">{label}:</span>{" "}
                <span>{description}</span>
              </li>
            );
          })}
        </ul>
      );
    }

    if (group.type === "bullet") {
      return (
        <ul className="scheme-bullet-list" key={index}>
          {group.lines.map((line, lIdx) => (
            <li key={lIdx}>{line.replace(/^[•●▪\-*]\s*/, "")}</li>
          ))}
        </ul>
      );
    }

    // paragraph
    return (
      <p className="scheme-content-line scheme-paragraph" key={index}>
        {group.lines[0]}
      </p>
    );
  };

  const renderScrapedContent = (value) => {
    if (!hasValue(value)) return null;

    const contentBlocks = removeDuplicateContent(value);
    const groups = groupBlocks(contentBlocks);

    return (
      <div className="scheme-details-text">
        {groups.map((group, index) => renderGroup(group, index))}
      </div>
    );
  };

  // ---------------------------------------------------------------
  // Resolve scheme duration for display.
  // ---------------------------------------------------------------
  const getDurationInfo = () => {
    if (!scheme) return { text: "Duration not specified", cleanedDetails: null, hasDates: false };

    let startDate = null;
    let endDate = null;
    let cleanedDetails = scheme.details;

    if (hasValue(scheme.start_date)) {
      const d = new Date(scheme.start_date);
      startDate = isNaN(d.getTime()) ? null : d;
    }
    if (hasValue(scheme.end_date)) {
      const d = new Date(scheme.end_date);
      endDate = isNaN(d.getTime()) ? null : d;
    }

    let usedExtraction = false;
    if (!startDate && !endDate) {
      const extracted = extractDateRange(scheme.details);
      startDate = extracted.startDate;
      endDate = extracted.endDate;
      cleanedDetails = extracted.cleanedText;
      usedExtraction = !!(extracted.startDate || extracted.endDate);
    }

    let text = "Duration not specified";
    if (startDate && endDate) {
      text = `${formatDate(startDate)} \u2013 ${formatDate(endDate)}`;
    } else if (startDate && !endDate) {
      text = `Started ${formatDate(startDate)} \u00b7 Ongoing`;
    } else if (!startDate && endDate) {
      text = `Ends ${formatDate(endDate)}`;
    }

    return { text, cleanedDetails, hasDates: usedExtraction || !!(startDate || endDate) };
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

  const { text: durationText, cleanedDetails, hasDates } = getDurationInfo();

  return (
    <div className="container py-5">
      <style>{`
        .scheme-details-text {
          font-size: 1rem;
          line-height: 1.7;
          color: #2b2b2b;
        }
        .scheme-content-block {
          margin-bottom: 1.25rem;
        }
        .scheme-content-line {
          margin-bottom: 0.75rem;
        }
        .scheme-paragraph {
          margin-bottom: 1rem;
        }
        .scheme-subheading {
          font-size: 1.05rem;
          font-weight: 700;
          margin-top: 1.5rem;
          margin-bottom: 0.6rem;
          color: #1a1a1a;
        }
        .scheme-bullet-list,
        .scheme-label-list {
          margin: 0 0 1rem 0;
          padding-left: 1.25rem;
        }
        .scheme-bullet-list li {
          margin-bottom: 0.5rem;
          line-height: 1.6;
        }
        .scheme-label-list {
          list-style: none;
          padding-left: 0;
        }
        .scheme-label-item {
          margin-bottom: 0.55rem;
          padding-left: 1.1rem;
          position: relative;
          line-height: 1.6;
        }
        .scheme-label-item::before {
          content: "\\2013";
          position: absolute;
          left: 0;
          color: #6c757d;
        }
        .scheme-label-text {
          font-weight: 600;
          color: #1a1a1a;
        }
        .scheme-table-wrap {
          margin: 0.5rem 0 1rem 0;
        }
        .scheme-data-table {
          font-size: 0.92rem;
          background: #fff;
        }
        .scheme-data-table td {
          padding: 0.5rem 0.75rem;
          vertical-align: top;
        }
        .scheme-section-title {
          margin-top: 0.25rem;
          margin-bottom: 1rem;
          font-weight: 700;
        }
        .scheme-section {
          margin-bottom: 2.5rem;
        }
      `}</style>

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
            <div className="mb-4 d-flex flex-wrap align-items-center gap-2">
              {hasValue(scheme.category) && (
                <span className="badge bg-success">{scheme.category}</span>
              )}
              {hasValue(scheme.state) && (
                <span className="badge bg-primary">{scheme.state}</span>
              )}
              {hasValue(scheme.status) && (
                <span className="badge bg-warning text-dark">{scheme.status}</span>
              )}
              <span className="badge bg-light text-dark border">{durationText}</span>
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
            {hasValue(hasDates ? cleanedDetails : scheme.details) && (
              <section id="details" className="scheme-section">
                <h3 className="scheme-section-title">Details</h3>
                {renderScrapedContent(hasDates ? cleanedDetails : scheme.details)}
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
