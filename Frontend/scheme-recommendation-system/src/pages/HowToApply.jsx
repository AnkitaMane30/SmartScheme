import "./CommonPages.css";
import {
  FaSearch,
  FaClipboardCheck,
  FaWpforms,
  FaUpload,
  FaCheckCircle,
  FaShieldAlt,
  FaClock,
  FaExclamationCircle,
  FaEnvelope,
  FaHeadset
} from "react-icons/fa";

export default function HowToApply() {
  return (
    <div className="page-wrapper">

      <div className="top-banner row align-items-center">
        <div className="col-md-6">
          <h1>How to Apply</h1>
          <p className="mt-3">
            Applying for government schemes is simple and completely online.
          </p>
        </div>

        <div className="col-md-6 text-center">
          <img src="https://cdn-icons-png.flaticon.com/512/942/942748.png" width="280"/>
        </div>
      </div>

      <h4 className="mb-4">Application Process</h4>

      <div className="row mb-5">
        {[
          {icon:<FaSearch/>, title:"Search Scheme", cls:"icon-blue"},
          {icon:<FaClipboardCheck/>, title:"Check Eligibility", cls:"icon-green"},
          {icon:<FaWpforms/>, title:"Fill Application", cls:"icon-purple"},
          {icon:<FaUpload/>, title:"Upload Documents", cls:"icon-yellow"},
          {icon:<FaCheckCircle/>, title:"Submit & Track", cls:"icon-green"},
        ].map((step,index)=>(
          <div className="col-md-2" key={index}>
            <div className="small-box text-center">
              <div className={`icon-circle ${step.cls}`}>{step.icon}</div>
              <h6>{step.title}</h6>
            </div>
          </div>
        ))}
      </div>

      <h4 className="mb-4">Important to Know</h4>

      <div className="row mb-5">
        <div className="col-md-3"><div className="small-box"><FaShieldAlt className="me-2 text-primary"/> Data Protected</div></div>
        <div className="col-md-3"><div className="small-box"><FaClock className="me-2 text-success"/> Keep Documents Ready</div></div>
        <div className="col-md-3"><div className="small-box"><FaExclamationCircle className="me-2 text-warning"/> Correct Information</div></div>
        <div className="col-md-3"><div className="small-box"><FaEnvelope className="me-2 text-danger"/> Email Updates</div></div>
      </div>

      <div className="section-card d-flex justify-content-between align-items-center">
        <div>
          <h4><FaHeadset className="me-2 text-primary"/>Need Help?</h4>
          <p>Support team is here to help you.</p>
        </div>

        <div>
          <button className="btn btn-outline-primary me-3">View FAQs</button>
          <button className="blue-btn">Contact Support</button>
        </div>
      </div>
    </div>
  );
}