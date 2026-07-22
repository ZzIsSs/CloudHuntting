import { useEffect, useRef } from 'react';
import styles from './ScoreBoard.module.css';

export default function ScoreBoard({ score }) {
  const boardRef = useRef(null);
  const prevScoreRef = useRef(score);

  useEffect(() => {
    if (score !== prevScoreRef.current) {
      prevScoreRef.current = score;
      const el = boardRef.current;
      if (el) {
        el.style.transform = 'scale(1.15)';
        const timeout = setTimeout(() => {
          el.style.transform = 'scale(1)';
        }, 150);
        return () => clearTimeout(timeout);
      }
    }
  }, [score]);

  return (
    <div className={styles.scoreBoard} ref={boardRef}>
      Săn mây: <span>{score}</span>
    </div>
  );
}
