// import { useState, useEffect } from "react";
// import { completeProfile, updateProfile, getProfile } from "../services/userServices";
// import { toast } from "react-toastify";
// import { useNavigate } from "react-router-dom";

// export default function Dashboard() {
//   const navigate = useNavigate();

//   const [user, setUser] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const [form, setForm] = useState({
//     age: "",
//     gender: "",
//     education_level: "",
//     income: "",
//     category: "",
//     state: "",
//     occupation: ""
//   });

//   // FETCH PROFILE
//   useEffect(() => {
//     const loadProfile = async () => {
//       const token = localStorage.getItem("token");

//       if (!token) {
//         toast.error("Please login first");
//         navigate("/login");
//         return;
//       }

//       const res = await getProfile();

//       if (res.error || !res.data) {
//         toast.error("Session expired. Please login again");
//         localStorage.clear();
//         navigate("/login");
//         return;
//       }

//       setUser(res.data);

//       setForm({
//         age: res.data.age || "",
//         gender: res.data.gender || "",
//         education_level: res.data.education_level || "",
//         income: res.data.income || "",
//         category: res.data.category || "",
//         state: res.data.state || "",
//         occupation: res.data.occupation || ""
//       });
//     };

//     loadProfile();
//   }, []);

//   const isCompleted = user?.profile_completed === 1;

//   const handleChange = (e) => {
//     setForm({ ...form, [e.target.name]: e.target.value });
//   };

//   const submit = async () => {
//     setLoading(true);

//     let result;

//     if (!isCompleted) {
//       result = await completeProfile(form);
//     } else {
//       result = await updateProfile({
//         income: form.income,
//         state: form.state,
//         occupation: form.occupation
//       });
//     }

//     setLoading(false);

//     if (result.error) {
//       return toast.error(result.error);
//     }

//     toast.success(result.data);

//     // GET LATEST PROFILE AGAIN FROM BACKEND
//     const freshProfile = await getProfile();

//     if (freshProfile.data) {
//       localStorage.setItem("user", JSON.stringify(freshProfile.data));
//       setUser(freshProfile.data);
//       window.dispatchEvent(new Event("userUpdated"));
//     }

//     // first time profile complete => move to schemes
//     if (!isCompleted) {
//       navigate("/schemes");
//     }
//   };

//   if (!user) {
//     return <div className="container mt-5 text-center">Loading Profile...</div>;
//   }

//   return (
//     <div className="container mt-4" style={{ maxWidth: "600px" }}>
//       <div className="card shadow p-4">
//         <h3 className="mb-4 text-center">
//           {!isCompleted ? "Complete Your Eligibility Profile" : "Update Eligibility Details"}
//         </h3>

//         {/* AGE */}
//         <input
//           name="age"
//           value={form.age}
//           placeholder="Age"
//           className="form-control mb-3"
//           onChange={handleChange}
//           disabled={isCompleted}
//         />

//         {/* GENDER */}
//         <select
//           name="gender"
//           value={form.gender}
//           className="form-control mb-3"
//           onChange={handleChange}
//           disabled={isCompleted}
//         >
//           <option value="">Select Gender</option>
//           <option>Male</option>
//           <option>Female</option>
//           <option>Other</option>
//         </select>

//         {/* EDUCATION */}
//         <select
//           name="education_level"
//           value={form.education_level}
//           className="form-control mb-3"
//           onChange={handleChange}
//           disabled={isCompleted}
//         >
//           <option value="">Select Education</option>
//           <option>Below 10th</option>
//           <option>10th Pass</option>
//           <option>12th Pass</option>
//           <option>Diploma</option>
//           <option>Graduate</option>
//           <option>Post Graduate</option>
//         </select>

//         {/* INCOME */}
//         <input
//           name="income"
//           value={form.income}
//           placeholder="Annual Income"
//           className="form-control mb-3"
//           onChange={handleChange}
//         />

//         {/* CATEGORY */}
//         <select
//           name="category"
//           value={form.category}
//           className="form-control mb-3"
//           onChange={handleChange}
//           disabled={isCompleted}
//         >
//           <option value="">Select Category</option>
//           <option>General</option>
//           <option>OBC</option>
//           <option>SC</option>
//           <option>ST</option>
//           <option>EWS</option>
//         </select>

//         {/* STATE */}
//         <select
//           name="state"
//           value={form.state}
//           className="form-control mb-3"
//           onChange={handleChange}
//         >
//           <option value="">Select State</option>
//           <option>Maharashtra</option>
//           <option>Gujarat</option>
//           <option>Karnataka</option>
//           <option>Tamil Nadu</option>
//           <option>Uttar Pradesh</option>
//         </select>

//         {/* OCCUPATION */}
//         <select
//           name="occupation"
//           value={form.occupation}
//           className="form-control mb-4"
//           onChange={handleChange}
//         >
//           <option value="">Select Occupation</option>
//           <option>Student</option>
//           <option>Farmer</option>
//           <option>Unemployed</option>
//           <option>Private Job</option>
//           <option>Government Job</option>
//           <option>Self Employed</option>
//         </select>

//         <button
//           className="btn btn-primary w-100"
//           onClick={submit}
//           disabled={loading}
//         >
//           {loading ? "Saving..." : !isCompleted ? "Save Profile" : "Update Details"}
//         </button>
//       </div>
//     </div>
//   );
// }