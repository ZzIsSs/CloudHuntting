import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'cloudHuntingScore';

export default function useScore() {
  const [score, setScore] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? parseInt(saved, 10) : 0;
  });

  const addScore = useCallback(() => {
    setScore((prev) => {
      const newScore = prev + 1;
      localStorage.setItem(STORAGE_KEY, newScore.toString());
      return newScore;
    });
  }, []);

  const resetScore = useCallback(() => {
    setScore(0);
    localStorage.setItem(STORAGE_KEY, '0');
  }, []);

  // Cross-tab sync
  useEffect(() => {
    const handleStorage = (e) => {
      if (e.key === STORAGE_KEY) {
        setScore(e.newValue ? parseInt(e.newValue, 10) : 0);
      }
    };

    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  return { score, addScore, resetScore };
}
