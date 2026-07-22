import styles from './VolumeControl.module.css';

export default function VolumeControl({ onVolumeChange, defaultVolume = 0.25 }) {
  const handleChange = (e) => {
    onVolumeChange(e.target.value);
  };

  return (
    <div className={styles.volumeControl}>
      <span role="img" aria-label="music">🎵</span>
      <input
        type="range"
        className={styles.slider}
        min="0"
        max="1"
        step="0.01"
        defaultValue={defaultVolume}
        onChange={handleChange}
      />
    </div>
  );
}
