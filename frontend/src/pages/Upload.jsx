export default function Upload({ next }) {
  return (
    <div>
      <h1>Upload Your Syllabus</h1>

      <div className="card">
        <input type="file" accept="application/pdf" />
        <p>Upload a PDF syllabus or paste text below</p>
      </div>

      <div className="card">
        <textarea
          placeholder="Paste syllabus text here..."
          style={{ width: "100%", height: "150px" }}
        />
      </div>

      <button onClick={next}>Next</button>
    </div>
  );
}