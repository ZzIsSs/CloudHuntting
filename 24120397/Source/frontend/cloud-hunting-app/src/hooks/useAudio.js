import { useCallback, useEffect } from 'react';

// Initialize Audio objects once at the module level
const globalBgMusic = new Audio('/sound/BGsound.mp3');
globalBgMusic.loop = true;
globalBgMusic.volume = 0.25;

const globalPopSound = new Audio('/sound/cloudTouching.mp3');
globalPopSound.volume = 0.7;

const globalBtnSound = new Audio('/sound/ButtonSelecting.mp3');
globalBtnSound.volume = 0.8;

export default function useAudio() {
  // Auto-play background music after first user interaction
  useEffect(() => {
    const handleInteraction = () => {
      globalBgMusic.play().catch(() => {});
    };

    document.body.addEventListener('click', handleInteraction, { once: true });
    document.body.addEventListener('keydown', handleInteraction, { once: true });
    document.body.addEventListener('touchstart', handleInteraction, { once: true });

    return () => {
      document.body.removeEventListener('click', handleInteraction);
      document.body.removeEventListener('keydown', handleInteraction);
      document.body.removeEventListener('touchstart', handleInteraction);
    };
  }, []);

  const playPop = useCallback(() => {
    globalPopSound.currentTime = 0;
    globalPopSound.play().catch(() => {});
  }, []);

  const playBtn = useCallback(() => {
    globalBtnSound.currentTime = 0;
    globalBtnSound.play().catch(() => {});
  }, []);

  const setVolume = useCallback((value) => {
    globalBgMusic.volume = parseFloat(value);
  }, []);

  return { playPop, playBtn, setVolume };
}
