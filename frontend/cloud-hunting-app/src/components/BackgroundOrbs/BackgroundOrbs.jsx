import styles from './BackgroundOrbs.module.css';

export default function BackgroundOrbs() {
  return (
    <>
      <div className={`${styles.orb} ${styles.orb1}`} />
      <div className={`${styles.orb} ${styles.orb2}`} />
      <div className={`${styles.orb} ${styles.orb3}`} />
    </>
  );
}
