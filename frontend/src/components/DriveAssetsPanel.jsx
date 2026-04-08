function DriveAssetsPanel({ assets, status }) {
  return (
    <section className="panel drive-assets-panel">
      <h2>Drive Attachments</h2>
      <p>Suggested resumes, portfolios, and resource files from Google Drive.</p>
      <div className="integration-status">
        <strong>Status:</strong>
        <span>{status}</span>
      </div>
      <ul className="drive-assets-list">
        {assets.length === 0 ? <li>No Drive files found yet.</li> : null}
        {assets.map((asset) => (
          <li key={asset.id}>
            <a href={asset.webViewLink} target="_blank" rel="noreferrer">
              {asset.name}
            </a>
            <span>{asset.mimeType}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default DriveAssetsPanel;
