// import { useEffect, useState } from "react";
// import { getAllSchemes } from "../services/schemeService";
// import { useNavigate } from "react-router-dom";

// import {
//   FaSearch,
//   FaSeedling,
//   FaCheckCircle,
// } from "react-icons/fa";

// export default function Schemes() {
//   const [schemes, setSchemes] = useState([]);
//   const [loading, setLoading] = useState(true);

//   const [searchText, setSearchText] = useState("");
//   const [selectedCategory, setSelectedCategory] = useState("");
//   const [selectedState, setSelectedState] = useState("");

//   const navigate = useNavigate();

//   useEffect(() => {
//     loadSchemes();
//   }, []);

//   const loadSchemes = async () => {
//     try {
//       const result = await getAllSchemes();

//       console.log("Schemes:", result);

//       if (Array.isArray(result)) {
//         setSchemes(result);
//       } else {
//         setSchemes([]);
//       }
//     } catch (error) {
//       console.log("Error loading schemes:", error);
//       setSchemes([]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Dynamic Categories
//   const categories = [
//     ...new Set(
//       schemes
//         .map((scheme) => scheme.category)
//         .filter(Boolean)
//     ),
//   ];

//   // Dynamic States
//   const states = [
//     ...new Set(
//       schemes
//         .map((scheme) => scheme.state)
//         .filter(Boolean)
//     ),
//   ];

//   // Filtering
//   const filteredSchemes = schemes.filter((scheme) => {
//     const matchesSearch =
//       (scheme.title || "")
//         .toLowerCase()
//         .includes(searchText.toLowerCase());

//     const matchesCategory =
//       selectedCategory === "" ||
//       scheme.category === selectedCategory;

//     const matchesState =
//       selectedState === "" ||
//       scheme.state === selectedState;

//     return (
//       matchesSearch &&
//       matchesCategory &&
//       matchesState
//     );
//   });

//   const resetFilters = () => {
//     setSearchText("");
//     setSelectedCategory("");
//     setSelectedState("");
//   };

//   if (loading) {
//     return (
//       <div className="text-center mt-5">
//         <h3>Loading Schemes...</h3>
//       </div>
//     );
//   }

//   return (
//     <div className="container-fluid p-0">
//       {/* SEARCH BAR */}
//       <div className="container mt-4">
//         <div className="d-flex shadow-sm p-3 rounded bg-white">
//           <FaSearch className="mt-2 me-3 text-secondary" />

//           <input
//             type="text"
//             className="form-control border-0"
//             placeholder="Search schemes..."
//             value={searchText}
//             onChange={(e) =>
//               setSearchText(e.target.value)
//             }
//           />
//         </div>
//       </div>

//       {/* MAIN CONTENT */}
//       <div className="container mt-5">
//         <div className="row">
//           {/* LEFT SIDE */}
//           <div className="col-md-9">
//             <h4 className="mb-4">
//               All Schemes ({filteredSchemes.length})
//             </h4>

//             {filteredSchemes.length === 0 ? (
//               <div className="alert alert-warning">
//                 No schemes found
//               </div>
//             ) : (
//               filteredSchemes.map((scheme) => (
//                 <div
//                   key={scheme.scheme_id}
//                   className="card mb-3 shadow-sm border-0"
//                 >
//                   <div className="card-body d-flex justify-content-between align-items-center">
//                     {/* LEFT */}
//                     <div className="d-flex gap-4 align-items-center">
//                       <div className="bg-light rounded p-4">
//                         <FaSeedling
//                           size={35}
//                           color="green"
//                         />
//                       </div>

//                       <div>
//                         <h5>{scheme.title}</h5>

//                         <p className="text-muted">
//                           {scheme.details
//                             ? scheme.details.substring(
//                                 0,
//                                 150
//                               ) + "..."
//                             : "No details available"}
//                         </p>

//                         <span className="badge bg-primary me-2">
//                           {scheme.department}
//                         </span>

//                         <span className="badge bg-success">
//                           {scheme.category}
//                         </span>

//                         <span className="badge bg-dark ms-2">
//                           {scheme.state || "India"}
//                         </span>
//                       </div>
//                     </div>

//                     {/* RIGHT */}
//                     <div className="text-end">
//                       <div className="text-success mb-2">
//                         <FaCheckCircle /> Available
//                       </div>

//                       {scheme.application_link && (
//                         <a
//                           href={scheme.application_link}
//                           target="_blank"
//                           rel="noreferrer"
//                           className="btn btn-primary mb-2"
//                         >
//                           Apply Now →
//                         </a>
//                       )}

//                       <br />

//                       <button
//                         className="btn btn-link text-decoration-none"
//                         onClick={() =>
//                           navigate(
//                             `/schemes/${scheme.scheme_id}`
//                           )
//                         }
//                       >
//                         View Details
//                       </button>
//                     </div>
//                   </div>
//                 </div>
//               ))
//             )}
//           </div>

//           {/* FILTER SECTION */}
//           <div className="col-md-3">
//             <div className="card p-4 shadow-sm border-0">
//               <h5>Filter</h5>

//               {/* Category */}
//               <label className="mt-3">
//                 Category
//               </label>

//               <select
//                 className="form-control"
//                 value={selectedCategory}
//                 onChange={(e) =>
//                   setSelectedCategory(e.target.value)
//                 }
//               >
//                 <option value="">
//                   All Categories
//                 </option>

//                 {categories.map((category, index) => (
//                   <option
//                     key={index}
//                     value={category}
//                   >
//                     {category}
//                   </option>
//                 ))}
//               </select>

//               {/* State */}
//               <label className="mt-4">
//                 State
//               </label>

//               <select
//                 className="form-control"
//                 value={selectedState}
//                 onChange={(e) =>
//                   setSelectedState(e.target.value)
//                 }
//               >
//                 <option value="">
//                   All States
//                 </option>

//                 {states.map((state, index) => (
//                   <option
//                     key={index}
//                     value={state}
//                   >
//                     {state}
//                   </option>
//                 ))}
//               </select>

//               <button
//                 className="btn btn-outline-secondary mt-4"
//                 onClick={resetFilters}
//               >
//                 Reset
//               </button>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
import { useEffect, useState } from "react";
import { getAllSchemes } from "../services/schemeService";
import { useNavigate, useSearchParams } from "react-router-dom";

import {
  FaSearch,
  FaSeedling,
  FaCheckCircle,
} from "react-icons/fa";

export default function Schemes() {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);

  const [searchText, setSearchText] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

  const navigate = useNavigate();

  // Reads/writes the ?category= query param in the URL, so a link
  // like /schemes?category=Water%20%26%20Sanitation lands with that
  // filter already applied instead of defaulting to "All".
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    loadSchemes();
  }, []);

  // Whenever the URL's query params change (including on first load,
  // and when the user clicks a category card elsewhere in the app
  // and gets routed back here), sync the filter dropdown to match.
  useEffect(() => {
    setSelectedCategory(searchParams.get("category") || "");
  }, [searchParams]);

  const loadSchemes = async () => {
    try {
      const result = await getAllSchemes();

      console.log("Schemes:", result);

      if (Array.isArray(result)) {
        setSchemes(result);
      } else {
        setSchemes([]);
      }
    } catch (error) {
      console.log("Error loading schemes:", error);
      setSchemes([]);
    } finally {
      setLoading(false);
    }
  };

  // Dynamic Categories
  const categories = [
    ...new Set(
      schemes
        .map((scheme) => scheme.category)
        .filter(Boolean)
    ),
  ];

  // Filtering
  const filteredSchemes = schemes.filter((scheme) => {
    const matchesSearch =
      (scheme.title || "")
        .toLowerCase()
        .includes(searchText.toLowerCase());

    const matchesCategory =
      selectedCategory === "" ||
      scheme.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Keep the dropdown change reflected back into the URL too, so the
  // page stays shareable/bookmarkable and the browser back button works.
  const handleCategoryChange = (value) => {
    setSelectedCategory(value);
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set("category", value);
    } else {
      next.delete("category");
    }
    setSearchParams(next);
  };

  const resetFilters = () => {
    setSearchText("");
    setSelectedCategory("");
    setSearchParams({});
  };

  // Heading shows the actual category name when one is selected,
  // instead of the generic "All Schemes".
  const listHeading = selectedCategory
    ? `${selectedCategory} Schemes (${filteredSchemes.length})`
    : `All Schemes (${filteredSchemes.length})`;

  if (loading) {
    return (
      <div className="text-center mt-5">
        <h3>Loading Schemes...</h3>
      </div>
    );
  }

  return (
    <div className="container-fluid p-0">
      {/* SEARCH BAR */}
      <div className="container mt-4">
        <div className="d-flex shadow-sm p-3 rounded bg-white">
          <FaSearch className="mt-2 me-3 text-secondary" />

          <input
            type="text"
            className="form-control border-0"
            placeholder="Search schemes..."
            value={searchText}
            onChange={(e) =>
              setSearchText(e.target.value)
            }
          />
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="container mt-5">
        <div className="row">
          {/* LEFT SIDE */}
          <div className="col-md-9">
            <h4 className="mb-4">
              {listHeading}
            </h4>

            {filteredSchemes.length === 0 ? (
              <div className="alert alert-warning">
                No schemes found
              </div>
            ) : (
              filteredSchemes.map((scheme) => (
                <div
                  key={scheme.scheme_id}
                  className="card mb-3 shadow-sm border-0"
                >
                  <div className="card-body d-flex justify-content-between align-items-center">
                    {/* LEFT */}
                    <div className="d-flex gap-4 align-items-center">
                      <div className="bg-light rounded p-4">
                        <FaSeedling
                          size={35}
                          color="green"
                        />
                      </div>

                      <div>
                        <h5>{scheme.title}</h5>

                        <p className="text-muted">
                          {scheme.details
                            ? scheme.details.substring(
                                0,
                                150
                              ) + "..."
                            : "No details available"}
                        </p>

                        <span className="badge bg-primary me-2">
                          {scheme.department}
                        </span>

                        <span className="badge bg-success">
                          {scheme.category}
                        </span>

                        <span className="badge bg-dark ms-2">
                          {scheme.state || "India"}
                        </span>
                      </div>
                    </div>

                    {/* RIGHT */}
                    <div className="text-end">
                      <div className="text-success mb-2">
                        <FaCheckCircle /> Available
                      </div>

                      {scheme.application_link && (
                        <a
                          href={scheme.application_link}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-primary mb-2"
                        >
                          Apply Now →
                        </a>
                      )}

                      <br />

                      <button
                        className="btn btn-link text-decoration-none"
                        onClick={() =>
                          navigate(
                            `/schemes/${scheme.scheme_id}`
                          )
                        }
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* FILTER SECTION */}
          <div className="col-md-3">
            <div className="card p-4 shadow-sm border-0">
              <h5>Filter</h5>

              {/* Category */}
              <label className="mt-3">
                Category
              </label>

              <select
                className="form-control"
                value={selectedCategory}
                onChange={(e) =>
                  handleCategoryChange(e.target.value)
                }
              >
                <option value="">
                  All Categories
                </option>

                {categories.map((category, index) => (
                  <option
                    key={index}
                    value={category}
                  >
                    {category}
                  </option>
                ))}
              </select>

              <button
                className="btn btn-outline-secondary mt-4"
                onClick={resetFilters}
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}