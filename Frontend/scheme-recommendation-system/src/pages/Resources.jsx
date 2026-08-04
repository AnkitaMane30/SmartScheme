import "./CommonPages.css";
import {
  FaFileAlt,
  FaClipboardCheck,
  FaFolderOpen,
  FaBullhorn,
  FaQuestionCircle
} from "react-icons/fa";

export default function Resources() {
  return (
    <div className="page-wrapper">

      <div className="top-banner row align-items-center">
        <div className="col-md-6">
          <h1>Resources</h1>
          <p className="mt-3">
            Helpful information, guides and documents to help you understand
            and apply for government schemes easily.
          </p>
        </div>

        <div className="col-md-6 text-center">
          <img src="https://cdn-icons-png.flaticon.com/512/2991/2991148.png" width="280" />
        </div>
      </div>

      <h4 className="mb-4">Browse by Category</h4>

      <div className="row mb-5">
        <div className="col-md-2">
          <div className="small-box text-center">
            <div className="icon-circle icon-blue"><FaFileAlt/></div>
            <h6>Guides & How To</h6>
          </div>
        </div>

        <div className="col-md-2">
          <div className="small-box text-center">
            <div className="icon-circle icon-green"><FaClipboardCheck/></div>
            <h6>Eligibility Criteria</h6>
          </div>
        </div>

        <div className="col-md-2">
          <div className="small-box text-center">
            <div className="icon-circle icon-purple"><FaFolderOpen/></div>
            <h6>Required Docs</h6>
          </div>
        </div>

        <div className="col-md-2">
          <div className="small-box text-center">
            <div className="icon-circle icon-yellow"><FaBullhorn/></div>
            <h6>Announcements</h6>
          </div>
        </div>

        <div className="col-md-2">
          <div className="small-box text-center">
            <div className="icon-circle icon-pink"><FaQuestionCircle/></div>
            <h6>FAQs</h6>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="section-card">
            <h5>Popular Resources</h5><hr/>
            <p><FaFileAlt className="me-2 text-primary"/>How to register on MyScheme <button className="btn btn-outline-primary btn-sm float-end">View</button></p>
            <p><FaClipboardCheck className="me-2 text-success"/>How to check eligibility <button className="btn btn-outline-primary btn-sm float-end">View</button></p>
            <p><FaFolderOpen className="me-2 text-warning"/>Required documents list <button className="btn btn-outline-primary btn-sm float-end">View</button></p>
            <p><FaFileAlt className="me-2 text-danger"/>Tips for successful application <button className="btn btn-outline-primary btn-sm float-end">View</button></p>
          </div>
        </div>

        <div className="col-md-6">
          <div className="section-card">
            <h5>Latest Updates</h5><hr/>
            <p><FaBullhorn className="me-2 text-primary"/>PM Kisan eKYC Deadline Extended <span className="float-end">10 May</span></p>
            <p><FaBullhorn className="me-2 text-success"/>New Scheme for Small Business <span className="float-end">06 May</span></p>
            <p><FaBullhorn className="me-2 text-warning"/>Scholarship Dates Announced <span className="float-end">02 May</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}