import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [asking, setAsking] = useState(false);
  const [editedData, setEditedData] = useState(null);
  const [reviewCompleted, setReviewCompleted] = useState(false);

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a PDF first");
      return;
    }

    setLoading(true);
    setResult(null);
    setReviewCompleted(false);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setResult(data);
      setEditedData(data.ai_extraction); // Initialize editedData with the original extraction data
    } catch (error) {
      console.error(error);
      alert("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      alert("Please enter a question");
      return;
    }

    setAsking(true);
    setAnswer(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      console.log("Status:", response.status);
      console.log("Response:", data);

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      setAnswer(data);
    } catch (error) {
      console.error("ASK ERROR:", error);
      alert(`Failed to get answer: ${error.message}`);
    } finally {
      setAsking(false);
    }
  };
  const approveReview = async () => {
    if (!editedData) {
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/review/approve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_data: editedData,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      console.log("Approval response:", data);
      setReviewCompleted(true);
      alert("Document approved and saved successfully.");
    } catch (error) {
      console.error("APPROVAL ERROR:", error);

      alert(`Failed to approve document: ${error.message}`);
    }
  };

  const extraction = result?.ai_extraction;
  const documentType = extraction?.document_type?.toLowerCase();
  const invoice = extraction?.invoice_details;
  const policy = extraction?.policy_details;
  const validation = result?.validation_result;
  const approval = result?.approval_result;
  const confidence = result?.confidence_result;
  const ingestion = result?.ingestion_result;
  const review = result?.review_result;

  return (
    <div className="app">
      {/* Header */}

      <header className="header">
        <div>
          <h1>AI Document Intelligence</h1>
          <p>Extract, validate and analyze business documents with AI.</p>
        </div>
      </header>

      {/* Upload Section */}

      <section className="upload-card">
        <div className="upload-icon">📄</div>

        <h2>Upload a Document</h2>

        <p>Upload a PDF and let AI analyze its contents.</p>

        <input
          id="file-upload"
          type="file"
          accept=".pdf"
          onChange={(event) => setFile(event.target.files[0])}
        />

        <label htmlFor="file-upload" className="file-button">
          Choose PDF
        </label>

        {file && (
          <div className="selected-file">
            <span>📎</span>
            <span>{file.name}</span>
          </div>
        )}

        <button
          className="upload-button"
          onClick={uploadFile}
          disabled={loading}
        >
          {loading ? "AI Processing..." : "Analyze Document"}
        </button>
      </section>

      {/* Results */}

      {result && (
        <main className="dashboard">
          {/* Overview */}

          <section className="section">
            <div className="section-title">
              <h2>Document Overview</h2>
            </div>

            {/* General document information */}
            <div className="overview-grid">
              <div className="info-card">
                <span className="label">File</span>
                <strong>{result.filename}</strong>
              </div>

              <div className="info-card">
                <span className="label">Pages</span>
                <strong>{result.page_count}</strong>
              </div>

              <div className="info-card">
                <span className="label">Document Type</span>
                <strong className="capitalize">
                  {extraction?.document_type || "Unknown"}
                </strong>
              </div>
            </div>

            {/* Resume-specific overview */}
            {documentType === "resume" && (
              <div className="overview-grid document-metrics">
                <div className="info-card">
                  <span className="label">Skills</span>
                  <strong>{extraction?.skills?.length || 0}</strong>
                </div>

                <div className="info-card">
                  <span className="label">Experience</span>
                  <strong>{extraction?.experience?.length || 0}</strong>
                </div>

                <div className="info-card">
                  <span className="label">Projects</span>
                  <strong>{extraction?.projects?.length || 0}</strong>
                </div>

                <div className="info-card">
                  <span className="label">Education</span>
                  <strong>{extraction?.education?.length || 0}</strong>
                </div>
              </div>
            )}

            {/* Invoice-specific overview */}
            {documentType === "invoice" && invoice && (
              <div className="overview-grid document-metrics">
                <div className="info-card">
                  <span className="label">Vendor</span>
                  <strong>{invoice.vendor_name || "Not found"}</strong>
                </div>

                <div className="info-card">
                  <span className="label">Invoice Number</span>
                  <strong>{invoice.invoice_number || "Not found"}</strong>
                </div>

                <div className="info-card">
                  <span className="label">Amount</span>
                  <strong>
                    {invoice.currency || ""}
                    {invoice.amount ?? "Not found"}
                  </strong>
                </div>

                <div className="info-card">
                  <span className="label">Approval</span>
                  <strong>
                    {approval?.status === "approval_required"
                      ? "Required"
                      : "Not Required"}
                  </strong>
                </div>
              </div>
            )}
          </section>

          {/* Policy Details */}
          {(documentType === "policy" || documentType === "expense policy") &&
            policy && (
              <section className="section policy-card">
                <div className="section-title">
                  <h2>Policy Details</h2>
                  <span>AI Extracted</span>
                </div>

                {/* Policy Metrics */}
                <div className="overview-grid">
                  <div className="info-card">
                    <span className="label">Submission Deadline</span>

                    <strong>
                      {policy.submission_deadline_days ?? "Not found"}
                      {policy.submission_deadline_days != null && " days"}
                    </strong>
                  </div>

                  <div className="info-card">
                    <span className="label">Approval Threshold</span>

                    <strong>
                      {policy.approval_threshold != null
                        ? `₹${policy.approval_threshold.toLocaleString()}`
                        : "Not found"}
                    </strong>
                  </div>

                  <div className="info-card">
                    <span className="label">Required Fields</span>

                    <strong>{policy.required_fields?.length || 0}</strong>
                  </div>
                </div>

                {/* Required Fields */}
                {policy.required_fields?.length > 0 && (
                  <div className="resume-section">
                    <h3>Required Fields</h3>

                    <div className="skill-list">
                      {policy.required_fields.map((field, index) => (
                        <span className="skill" key={index}>
                          ✓ {field}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

          {/* Resume details*/}
          {documentType === "resume" && (
            <section className="section resume-card">
              <div className="section-title">
                <h2>Resume Details</h2>
                <span>AI Extracted</span>
              </div>

              {/* Personal Information */}
              <div className="resume-header">
                <h3>{extraction?.name || "Name not found"}</h3>

                <div className="contact-row">
                  {extraction?.email && <span>📧 {extraction.email}</span>}

                  {extraction?.phone && <span>📱 {extraction.phone}</span>}
                </div>
              </div>

              {/* Skills */}
              {extraction?.skills?.length > 0 && (
                <div className="resume-section">
                  <h3>Skills</h3>

                  <div className="skill-list">
                    {extraction.skills.map((skill, index) => (
                      <span className="skill" key={index}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience */}
              {extraction?.experience?.length > 0 && (
                <div className="resume-section">
                  <h3>Experience</h3>

                  {extraction.experience.map((item, index) => (
                    <div className="resume-item" key={index}>
                      <div className="resume-item-header">
                        <div>
                          <h4>{item.role || "Role not specified"}</h4>
                          <p>{item.company || "Company not specified"}</p>
                        </div>

                        <span>{item.period}</span>
                      </div>

                      {item.location && (
                        <p className="resume-location">📍 {item.location}</p>
                      )}

                      {item.description?.length > 0 && (
                        <ul>
                          {item.description.map((description, i) => (
                            <li key={i}>{description}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Projects */}
              {extraction?.projects?.length > 0 && (
                <div className="resume-section">
                  <h3>Projects</h3>

                  {extraction.projects.map((project, index) => (
                    <div className="resume-item" key={index}>
                      <h4>{project.name || "Project"}</h4>

                      {project.tech_stack?.length > 0 && (
                        <div className="skill-list">
                          {project.tech_stack.map((tech, i) => (
                            <span className="skill" key={i}>
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}

                      {project.description?.length > 0 && (
                        <ul>
                          {project.description.map((description, i) => (
                            <li key={i}>{description}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Education */}
              {extraction?.education?.length > 0 && (
                <div className="resume-section">
                  <h3>Education</h3>

                  {extraction.education.map((education, index) => (
                    <div className="education-card" key={index}>
                      <h4>{education.degree || "Degree not specified"}</h4>

                      <p>
                        {education.institution || "Institution not specified"}
                      </p>

                      {education.period && <span>{education.period}</span>}

                      {education.grade && <p>Grade: {education.grade}</p>}

                      {education.gpa && <p>GPA: {education.gpa}</p>}
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

          {/* Invoice Details */}

          {invoice && (
            <section className="section">
              <div className="section-title">
                <h2>Invoice Details</h2>
              </div>

              <div className="details-grid">
                <div className="detail-item">
                  <span>Vendor</span>
                  <strong>{invoice.vendor_name || "—"}</strong>
                </div>

                <div className="detail-item">
                  <span>Invoice Number</span>
                  <strong>{invoice.invoice_number || "—"}</strong>
                </div>

                <div className="detail-item">
                  <span>Invoice Date</span>
                  <strong>{invoice.invoice_date || "—"}</strong>
                </div>

                <div className="detail-item">
                  <span>Due Date</span>
                  <strong>{invoice.due_date || "—"}</strong>
                </div>

                <div className="detail-item">
                  <span>Amount</span>
                  <strong>
                    {invoice.currency === "INR" ? "₹" : ""}
                    {invoice.amount?.toLocaleString() || "—"}
                  </strong>
                </div>

                <div className="detail-item">
                  <span>Tax</span>
                  <strong>
                    {invoice.currency === "INR" ? "₹" : ""}
                    {invoice.tax?.toLocaleString() || "—"}
                  </strong>
                </div>

                <div className="detail-item">
                  <span>Currency</span>
                  <strong>{invoice.currency || "—"}</strong>
                </div>
              </div>
            </section>
          )}

          {/* Status Cards */}

          <div className="status-grid">
            {/* Validation */}

            <section className="status-card">
              <div className="card-heading">
                <h2>Validation</h2>

                <span
                  className={`status-badge ${
                    validation?.status === "passed" ? "success" : "warning"
                  }`}
                >
                  {validation?.status}
                </span>
              </div>

              {validation?.missing_fields?.length > 0 && (
                <div>
                  <h4>Missing Fields</h4>

                  <ul>
                    {validation.missing_fields.map((field, index) => (
                      <li key={index}>{field}</li>
                    ))}
                  </ul>
                </div>
              )}

              {validation?.warnings?.length > 0 && (
                <div>
                  <h4>Warnings</h4>

                  <ul>
                    {validation.warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              {validation?.errors?.length > 0 && (
                <div>
                  <h4>Errors</h4>

                  <ul>
                    {validation.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}

              {validation?.status === "passed" && (
                <p className="success-text">
                  ✓ All required validation checks passed.
                </p>
              )}
            </section>
            {/* Human Review */}
            {review && (
              <section className="section review-card">
                <div className="section-title">
                  <h2>AI Review Status</h2>
                  <span>AI Decision</span>
                </div>

                <div
                  className={`review-status ${
                    review.review_required
                      ? "review-required"
                      : "review-approved"
                  }`}
                >
                  <div className="review-status-icon">
                    {reviewCompleted
                      ? "✓"
                      : review.review_required
                        ? "⚠️"
                        : "✓"}
                  </div>

                  <div>
                    <h3>
                      {reviewCompleted
                        ? "Review Completed"
                        : review.review_required
                          ? "Manual Review Required"
                          : "AI Review Complete"}
                    </h3>

                    <p>
                      {reviewCompleted
                        ? "The corrected document data has been verified and saved."
                        : review.review_required
                          ? "This document requires manual verification."
                          : "No manual correction is required."}
                    </p>
                  </div>
                </div>

                {review.reasons?.length > 0 && (
                  <div className="review-reasons">
                    <h3>Review Reasons</h3>

                    <ul>
                      {review.reasons.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>
            )}
            {/* Review Extracted Data */}
            {review?.review_required &&
              editedData &&
              documentType === "invoice" &&
              editedData.invoice_details && (
                <section className="section">
                  <div className="section-title">
                    <h2>Review Extracted Data</h2>
                    <span>Manual Correction</span>
                  </div>

                  <div className="review-form">
                    <div className="form-group">
                      <label>Vendor Name</label>

                      <input
                        type="text"
                        value={editedData.invoice_details.vendor_name || ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              vendor_name: e.target.value,
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Invoice Number</label>

                      <input
                        type="text"
                        value={editedData.invoice_details.invoice_number || ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              invoice_number: e.target.value,
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Invoice Date</label>

                      <input
                        type="text"
                        value={editedData.invoice_details.invoice_date || ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              invoice_date: e.target.value,
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Due Date</label>

                      <input
                        type="text"
                        value={editedData.invoice_details.due_date || ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              due_date: e.target.value,
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Amount</label>

                      <input
                        type="number"
                        value={editedData.invoice_details.amount ?? ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              amount:
                                e.target.value === ""
                                  ? null
                                  : Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Tax</label>

                      <input
                        type="number"
                        value={editedData.invoice_details.tax ?? ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              tax:
                                e.target.value === ""
                                  ? null
                                  : Number(e.target.value),
                            },
                          })
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label>Currency</label>

                      <input
                        type="text"
                        value={editedData.invoice_details.currency || ""}
                        onChange={(e) =>
                          setEditedData({
                            ...editedData,
                            invoice_details: {
                              ...editedData.invoice_details,
                              currency: e.target.value,
                            },
                          })
                        }
                      />
                    </div>
                    <button className="approve-button" onClick={approveReview}>
                      ✓ Approve & Save
                    </button>
                  </div>
                </section>
              )}
            {/* Approval */}

            <section className="status-card">
              <div className="card-heading">
                <h2>Approval</h2>

                {approval && (
                  <span
                    className={`status-badge ${
                      approval.status === "approval_required"
                        ? "warning"
                        : "success"
                    }`}
                  >
                    {approval.status.replaceAll("_", " ")}
                  </span>
                )}
              </div>

              {approval ? (
                <>
                  {approval.invoice_amount !== undefined && (
                    <div className="approval-values">
                      <div>
                        <span>Invoice Amount</span>
                        <strong>
                          ₹{approval.invoice_amount.toLocaleString()}
                        </strong>
                      </div>

                      <div>
                        <span>Approval Threshold</span>
                        <strong>
                          ₹{approval.approval_threshold.toLocaleString()}
                        </strong>
                      </div>
                    </div>
                  )}

                  <p className="approval-message">{approval.message}</p>
                </>
              ) : (
                <p>Approval check not applicable.</p>
              )}
            </section>
          </div>

          {/* Confidence */}

          <section className="section">
            <div className="section-title">
              <h2>AI Extraction Confidence</h2>
              <span>Heuristic confidence score</span>
            </div>

            <div className="confidence-list">
              {confidence &&
                Object.entries(confidence).map(([field, information]) => {
                  const percentage = Math.round(information.confidence * 100);

                  return (
                    <div className="confidence-item" key={field}>
                      <div className="confidence-header">
                        <span>{field.replaceAll("_", " ")}</span>

                        <strong>{percentage}%</strong>
                      </div>

                      <div className="progress-background">
                        <div
                          className="progress-bar"
                          style={{
                            width: `${percentage}%`,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </section>

          {/* RAG */}

          <section className="section rag-card">
            <div>
              <h2>RAG Ingestion</h2>
              <p>Document successfully processed for retrieval.</p>
            </div>

            <div className="rag-stat">
              <strong>{ingestion?.chunks_created || 0}</strong>

              <span>Chunks Created</span>
            </div>
          </section>
          {/* Document Q&A */}

          <section className="section qa-card">
            <div className="section-title">
              <h2>Ask Your Documents</h2>
              <span>Powered by RAG</span>
            </div>

            <div className="question-box">
              <input
                type="text"
                placeholder="Ask a question about your documents..."
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    askQuestion();
                  }
                }}
              />

              <button onClick={askQuestion} disabled={asking}>
                {asking ? "Thinking..." : "Ask"}
              </button>
            </div>

            {answer && (
              <div className="answer-box">
                <h3>Answer</h3>

                <p>{answer.answer}</p>

                <h3>Sources</h3>

                {answer.sources?.map((source, index) => (
                  <div className="source" key={index}>
                    <strong>{source.source_file}</strong>

                    <span>Chunk {source.chunk_number}</span>

                    <p>{source.text}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

export default App;
