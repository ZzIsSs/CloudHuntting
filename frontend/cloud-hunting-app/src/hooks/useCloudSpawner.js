import { useState, useCallback, useEffect, useRef } from 'react';

const CLOUD_COLORS = [
  'linear-gradient(to bottom, #ffffff, #f1f5f9)',
  'linear-gradient(to bottom, #ffffff, #e0f2fe)',
  'linear-gradient(to bottom, #f8fafc, #e2e8f0)',
];

function createCloud() {
  return {
    id: Date.now() + Math.random(),
    color: CLOUD_COLORS[Math.floor(Math.random() * CLOUD_COLORS.length)],
    startY: Math.random() * (window.innerHeight - 150) + 50,
    fromLeft: Math.random() > 0.5,
    scale: 0.6 + Math.random() * 0.6,
    duration: 8 + Math.random() * 7,
    amplitude: 15 + Math.random() * 20,
    frequency: 1.5 + Math.random() * 2,
  };
}

export default function useCloudSpawner(spawnRate = 'normal') {
  const [clouds, setClouds] = useState([]);
  const timeoutsRef = useRef([]);
  const intervalRef = useRef(null);

  const spawnCloud = useCallback(() => {
    const cloud = createCloud();
    setClouds((prev) => [...prev, cloud]);
    return cloud;
  }, []);

  const removeCloud = useCallback((id) => {
    setClouds((prev) => prev.filter((c) => c.id !== id));
  }, []);

  // Initial spawn on mount
  useEffect(() => {
    const initialCount = 3;
    for (let i = 0; i < initialCount; i++) {
      const timeout = setTimeout(() => {
        spawnCloud();
      }, i * 500);
      timeoutsRef.current.push(timeout);
    }

    return () => {
      timeoutsRef.current.forEach(clearTimeout);
      timeoutsRef.current = [];
    };
  }, [spawnCloud]);

  // Auto-spawn interval
  useEffect(() => {
    const isNormal = spawnRate === 'normal';
    const intervalMs = isNormal ? 3000 : 6000;

    intervalRef.current = setInterval(() => {
      const minClouds = isNormal ? 3 : 1;
      const maxClouds = isNormal ? 5 : 2;
      const count = Math.floor(Math.random() * (maxClouds - minClouds + 1)) + minClouds;

      for (let i = 0; i < count; i++) {
        const delay = Math.random() * 2000;
        const timeout = setTimeout(() => {
          spawnCloud();
        }, delay);
        timeoutsRef.current.push(timeout);
      }
    }, intervalMs);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      timeoutsRef.current.forEach(clearTimeout);
      timeoutsRef.current = [];
    };
  }, [spawnRate, spawnCloud]);

  return { clouds, spawnCloud, removeCloud };
}
