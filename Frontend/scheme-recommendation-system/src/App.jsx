import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import FindSchemes from "./pages/FindSchemes";
import SchemeDetails from "./pages/SchemeDetails";

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
        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/schemes" element={<Schemes />} />
        <Route path="/schemes/:id" element={<SchemeDetails />} />
        <Route path="/about" element={<About />} />
        <Route path="/findscheme" element={<FindSchemes />}/>
        
      </Routes>
    </BrowserRouter>
  );
}

export default App;