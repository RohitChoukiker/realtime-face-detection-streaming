import React from "react";
import styles from "../styles/ROIPanel.module.css";

function StatCard({ label, value }) {
  return (
    <div className={styles.statCard}>
      <span className={styles.statLabel}>{label}</span>
      <span className={styles.statValue}>{value ?? "—"}</span>
    </div>
  );
}

export default function ROIPanel({ roiList, stats, total, loading, sessionId, liveROI }) {
  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>ROI Data</h2>
        {loading && <span className={styles.loader}>⟳</span>}
      </div>


      {sessionId && (
        <p className={styles.sessionId}>
          Session: <code>{sessionId.slice(0, 8)}…</code>
          <span className={styles.totalBadge}>{total} total detections</span>
        </p>
      )}

      {liveROI && (
        <div className={styles.liveROI}>
          <h3 className={styles.sectionTitle}>Current Frame</h3>
          <div className={styles.liveGrid}>
            <div className={styles.liveItem}>
              <span>X</span><strong>{liveROI.x}px</strong>
            </div>
            <div className={styles.liveItem}>
              <span>Y</span><strong>{liveROI.y}px</strong>
            </div>
            <div className={styles.liveItem}>
              <span>Width</span><strong>{liveROI.width}px</strong>
            </div>
            <div className={styles.liveItem}>
              <span>Height</span><strong>{liveROI.height}px</strong>
            </div>
            <div className={styles.liveItem}>
              <span>Confidence</span>
              <strong className={styles.confidence}>
                {(liveROI.confidence * 100).toFixed(1)}%
              </strong>
            </div>
          </div>
        </div>
      )}

 
      {stats && (
        <div className={styles.statsGrid}>
          <StatCard label="Total Detections" value={stats.total_detections} />
          <StatCard label="Avg Confidence" value={stats.avg_confidence ? `${(stats.avg_confidence * 100).toFixed(1)}%` : null} />
          <StatCard label="Avg Width" value={stats.avg_width ? `${Math.round(stats.avg_width)}px` : null} />
          <StatCard label="Avg Height" value={stats.avg_height ? `${Math.round(stats.avg_height)}px` : null} />
        </div>
      )}

  
      <h3 className={styles.sectionTitle}>Recent Detections</h3>
      {roiList.length === 0 ? (
        <p className={styles.empty}>
          {sessionId ? "No detections yet…" : "Start a session to see data"}
        </p>
      ) : (
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Frame</th>
                <th>X</th>
                <th>Y</th>
                <th>W</th>
                <th>H</th>
                <th>Conf</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {roiList.map((roi) => (
                <tr key={roi.id} className={styles.row}>
                  <td>{roi.frame_id}</td>
                  <td>{roi.x}</td>
                  <td>{roi.y}</td>
                  <td>{roi.width}</td>
                  <td>{roi.height}</td>
                  <td>
                    <span className={styles.confPill}>
                      {(roi.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className={styles.timestamp}>
                    {new Date(roi.detected_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
