import React from "react";
import styles from "../styles/Header.module.css";

export default function Header({ backendStatus }) {
  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.logo}></span>
        <div>
          <h1 className={styles.title}>Face Detection System</h1>
       
        </div>
      </div>
      <div className={styles.right}>
        <span className={`${styles.statusDot} ${backendStatus === "ok" ? styles.green : styles.red}`} />
        <span className={styles.statusText}>
          Backend {backendStatus === "ok" ? "Connected" : "Offline"}
        </span>
      </div>
    </header>
  );
}
