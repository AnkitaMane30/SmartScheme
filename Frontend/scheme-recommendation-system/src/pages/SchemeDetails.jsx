// import { useEffect, useState } from "react";
// import { useParams } from "react-router-dom";
// import { getSchemeById } from "../services/schemeService";

// export default function SchemeDetails() {
//   const { id } = useParams();

//   const [scheme, setScheme] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     loadScheme();
//   }, []);

//   const loadScheme = async () => {
//     try {
//       const result = await getSchemeById(id);

//       console.log(result);

//       setScheme(result);
//     } catch (error) {
//       console.log(error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   if (loading) {
//     return (
//       <div className="text-center mt-5">
//         <h3>Loading...</h3>
//       </div>
//     );
//   }

//   if (!scheme) {
//     return (
//       <div className="text-center mt-5">
//         <h3>Scheme Not Found</h3>
//       </div>
//     );
//   }

//   return (
//     <div className="container-fluid bg-light min-vh-100 py-4">

//       <div className="container">

//         {/* Back Button */}
//         <button
//           className="btn btn-link text-decoration-none mb-4"
//           onClick={() => window.history.back()}
//         >
//           ← Back
//         </button>

//         <div className="row">

//           {/* LEFT MENU */}
//           <div className="col-md-3">

//             <div className="card border-0 shadow-sm">

//               <div className="list-group list-group-flush">

//                 <a href="#details" className="list-group-item">
//                   Details
//                 </a>

//                 <a href="#benefits" className="list-group-item">
//                   Benefits
//                 </a>

//                 <a href="#eligibility" className="list-group-item">
//                   Eligibility
//                 </a>

//                 <a href="#exclusion" className="list-group-item">
//                   Exclusions
//                 </a>

//                 <a href="#documents" className="list-group-item">
//                   Documents Required
//                 </a>

//                 <a href="#process" className="list-group-item">
//                   Application Process
//                 </a>

//               </div>

//             </div>

//           </div>

//           {/* RIGHT CONTENT */}
//           <div className="col-md-9">

//             <div className="card border-0 shadow-sm p-4">

//               {/* Department */}
//               <p className="text-muted">
//                 {scheme.department}
//               </p>

//               {/* Title */}
//               <h2 className="fw-bold mb-3">
//                 {scheme.title}
//               </h2>

//               {/* Tags */}
//               <div className="mb-4">

//                 <span className="badge bg-success me-2">
//                   {scheme.category}
//                 </span>

//                 <span className="badge bg-primary me-2">
//                   {scheme.state}
//                 </span>

//                 <span className="badge bg-warning text-dark">
//                   {scheme.status}
//                 </span>

//               </div>

//               {/* Buttons */}
//               <div className="mb-4">

//                 <button
//                   className="btn btn-outline-primary me-3"
//                 >
//                   Check Eligibility
//                 </button>

//                 {scheme.application_link && (
//                   <a
//                     href={scheme.application_link}
//                     target="_blank"
//                     rel="noreferrer"
//                     className="btn btn-primary"
//                   >
//                     Apply Now
//                   </a>
//                 )}

//               </div>

//               <hr />

//               {/* DETAILS */}
//               <section id="details" className="mb-5">
//                 <h3>Details</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.details || "Not Available"}
//                 </p>
//               </section>

//               {/* BENEFITS */}
//               <section id="benefits" className="mb-5">
//                 <h3>Benefits</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.benefits || "Not Available"}
//                 </p>
//               </section>

//               {/* ELIGIBILITY */}
//               <section id="eligibility" className="mb-5">
//                 <h3>Eligibility</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.eligibility || "Not Available"}
//                 </p>
//               </section>

//               {/* EXCLUSION */}
//               <section id="exclusion" className="mb-5">
//                 <h3>Exclusions</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.exclusion || "Not Available"}
//                 </p>
//               </section>

//               {/* DOCUMENTS */}
//               <section id="documents" className="mb-5">
//                 <h3>Documents Required</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.documents_required || "Not Available"}
//                 </p>
//               </section>

//               {/* APPLICATION PROCESS */}
//               <section id="process" className="mb-5">
//                 <h3>Application Process</h3>

//                 <p style={{ whiteSpace: "pre-wrap" }}>
//                   {scheme.application_process || "Not Available"}
//                 </p>
//               </section>

//               {/* EXTRA INFO */}

//               <hr />

//               <div className="row">

//                 <div className="col-md-6">
//                   <strong>Min Age:</strong>{" "}
//                   {scheme.min_age || "-"}
//                 </div>

//                 <div className="col-md-6">
//                   <strong>Max Age:</strong>{" "}
//                   {scheme.max_age || "-"}
//                 </div>

//                 <div className="col-md-6 mt-3">
//                   <strong>Gender:</strong>{" "}
//                   {scheme.gender || "All"}
//                 </div>

//                 <div className="col-md-6 mt-3">
//                   <strong>Target Group:</strong>{" "}
//                   {scheme.target_group || "-"}
//                 </div>

//                 <div className="col-md-6 mt-3">
//                   <strong>Min Income:</strong>{" "}
//                   {scheme.min_income || "-"}
//                 </div>

//                 <div className="col-md-6 mt-3">
//                   <strong>Max Income:</strong>{" "}
//                   {scheme.max_income || "-"}
//                 </div>

//               </div>

//             </div>

//           </div>

//         </div>

//       </div>

//     </div>
//   );
// }

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSchemeById } from "../services/schemeService";
import { useNavigate } from "react-router-dom";  

export default function SchemeDetails() {
  const { id } = useParams();

  const [scheme, setScheme] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadScheme();
  }, []);

  const loadScheme = async () => {
    try {
      const result = await getSchemeById(id);
      setScheme(result);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to check if value exists
  const hasValue = (value) => {
    return (
      value &&
      value.toString().trim() !== "" &&
      value !== "Not Available" &&
      value !== "NA" &&
      value !== "N/A"
    );
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <h3>Loading...</h3>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="text-center mt-5">
        <h3>Scheme Not Found</h3>
      </div>
    );
  }

  return (
    <div className="container-fluid bg-light min-vh-100 py-4">
      <div className="container">
        {/* Back Button */}
        <button
  className="btn btn-link text-decoration-none mb-4"
  onClick={() => navigate("/schemes")}
>
  ← Back
</button> 

        <div className="row">
          {/* LEFT MENU */}
          <div className="col-md-3">
            <div
              className="card border-0 shadow-sm sticky-top"
              style={{
                top: "20px",
                maxHeight: "90vh",
                overflowY: "auto",
              }}>
              <div className="list-group list-group-flush">
                <a href="#details" className="list-group-item">
                  Details
                </a>

                {hasValue(scheme.benefits) && (
                  <a href="#benefits" className="list-group-item">
                    Benefits
                  </a>
                )}

                {hasValue(scheme.eligibility) && (
                  <a href="#eligibility" className="list-group-item">
                    Eligibility
                  </a>
                )}

                {hasValue(scheme.exclusion) && (
                  <a href="#exclusion" className="list-group-item">
                    Exclusions
                  </a>
                )}

                {hasValue(scheme.documents_required) && (
                  <a href="#documents" className="list-group-item">
                    Documents Required
                  </a>
                )}

                {hasValue(scheme.application_process) && (
                  <a href="#process" className="list-group-item">
                    Application Process
                  </a>
                )}
                {(hasValue(scheme.min_age) ||
  hasValue(scheme.max_age) ||
  hasValue(scheme.gender) ||
  hasValue(scheme.target_group) ||
  hasValue(scheme.min_income) ||
  hasValue(scheme.max_income)) && (
  <a href="#additional-info" className="list-group-item">
    Additional Information
  </a>
)}
              </div>
            </div>
          </div>

          {/* RIGHT CONTENT */}
          <div className="col-md-9">
            <div className="card border-0 shadow-sm p-4">
              {/* Department */}
              {hasValue(scheme.department) && (
                <p className="text-muted">{scheme.department}</p>
              )}

              {/* Title */}
              <h2 className="fw-bold mb-3">{scheme.title}</h2>

              {/* Tags */}
              <div className="mb-4">
                {hasValue(scheme.category) && (
                  <span className="badge bg-success me-2">
                    {scheme.category}
                  </span>
                )}

                {hasValue(scheme.state) && (
                  <span className="badge bg-primary me-2">
                    {scheme.state}
                  </span>
                )}

                {hasValue(scheme.status) && (
                  <span className="badge bg-warning text-dark">
                    {scheme.status}
                  </span>
                )}
              </div>

              {/* Buttons */}
              <div className="mb-4">
                <button className="btn btn-outline-primary me-3">
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

              <hr />

              {/* DETAILS */}
              <section id="details" className="mb-5">
                <h3>Details</h3>

                <p style={{ whiteSpace: "pre-wrap" }}>
                  {scheme.details}
                </p>
              </section>

              {/* BENEFITS */}
              {hasValue(scheme.benefits) && (
                <section id="benefits" className="mb-5">
                  <h3>Benefits</h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {scheme.benefits}
                  </p>
                </section>
              )}

              {/* ELIGIBILITY */}
              {hasValue(scheme.eligibility) && (
                <section id="eligibility" className="mb-5">
                  <h3>Eligibility</h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {scheme.eligibility}
                  </p>
                </section>
              )}

              

              {/* EXCLUSIONS */}
              {hasValue(scheme.exclusion) && (
                <section id="exclusion" className="mb-5">
                  <h3>Exclusions</h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {scheme.exclusion}
                  </p>
                </section>
              )}

              {/* DOCUMENTS */}
              {hasValue(scheme.documents_required) && (
                <section id="documents" className="mb-5">
                  <h3>Documents Required</h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {scheme.documents_required}
                  </p>
                </section>
              )}

              {/* APPLICATION PROCESS */}
              {hasValue(scheme.application_process) && (
                <section id="process" className="mb-5">
                  <h3>Application Process</h3>

                  <p style={{ whiteSpace: "pre-wrap" }}>
                    {scheme.application_process}
                  </p>
                </section>
              )}

              {(hasValue(scheme.min_age) ||
  hasValue(scheme.max_age) ||
  hasValue(scheme.gender) ||
  hasValue(scheme.target_group) ||
  hasValue(scheme.min_income) ||
  hasValue(scheme.max_income)) && (
  <section id="additional-info" className="mb-5">

    <h3>Additional Information</h3>

    <div className="row">

      {hasValue(scheme.min_age) && (
        <div className="col-md-6 mt-3">
          <strong>Minimum Age:</strong> {scheme.min_age}
        </div>
      )}

      {hasValue(scheme.max_age) && (
        <div className="col-md-6 mt-3">
          <strong>Maximum Age:</strong> {scheme.max_age}
        </div>
      )}

      <div className="col-md-6 mt-3">
        <strong>Gender:</strong> {scheme.gender || "All"}
      </div>

      <div className="col-md-6 mt-3">
        <strong>Target Group:</strong> {scheme.target_group || "Citizens"}
      </div>

      {hasValue(scheme.min_income) && (
        <div className="col-md-6 mt-3">
          <strong>Minimum Income:</strong> ₹ {scheme.min_income}
        </div>
      )}

      {hasValue(scheme.max_income) && (
        <div className="col-md-6 mt-3">
          <strong>Maximum Income:</strong> ₹ {scheme.max_income}
        </div>
      )}

    </div>

  </section>
)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

