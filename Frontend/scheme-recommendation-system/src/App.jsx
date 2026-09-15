import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import FindSchemes from "./pages/FindSchemes";
import SchemeDetails from "./pages/SchemeDetails";
import RecommendationStart from "./pages/RecommendationStart";
import UpdateProfile from "./pages/UpdateProfile";
import Recommendations from "./pages/Recommendations";

function App() {

  return (
    <BrowserRouter>

      <Navbar />

      <ToastContainer
        position="top-right"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        pauseOnHover
        theme="colored"
      />

      <Routes>

        {/* ================= HOME ================= */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* ================= AUTH ================= */}
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        {/* ================= RECOMMENDATION FLOW ================= */}

        <Route
          path="/recommendation-start"
          element={<RecommendationStart />}
        />

        <Route
          path="/findscheme"
          element={<FindSchemes />}
        />

        <Route
          path="/update-profile"
          element={<UpdateProfile />}
        />

        {/* ================= SCHEMES ================= */}

        <Route
          path="/schemes"
          element={<Schemes />}
        />

        <Route
          path="/schemes/:id"
          element={<SchemeDetails />}
        />

        {/* ================= ABOUT ================= */}

        <Route
          path="/about"
          element={<About />}
        />

        <Route path="/recommendations" element={<Recommendations />} />

      </Routes>

    </BrowserRouter>
  );
}

export default App;