import { useRef, useEffect, useCallback } from 'react';
import styles from './Cloud.module.css';

export default function Cloud({
  id,
  color,
  startY,
  fromLeft,
  scale,
  duration,
  amplitude,
  frequency,
  onDissipate,
  onExpire,
}) {
  const cloudRef = useRef(null);
  const animationRef = useRef(null);
  const isDissipatedRef = useRef(false);
  const autoRemoveTimerRef = useRef(null);

  const dissipate = useCallback(() => {
    if (isDissipatedRef.current) return;
    isDissipatedRef.current = true;

    const el = cloudRef.current;
    if (!el) return;

    // If animation still active, get position before cancelling
    if (animationRef.current) {
      const computedStyle = window.getComputedStyle(el);
      if (computedStyle.transform && computedStyle.transform !== 'none') {
        const matrix = new DOMMatrixReadOnly(computedStyle.transform);
        el.style.left = `${el.offsetLeft + matrix.m41}px`;
        el.style.top = `${el.offsetTop + matrix.m42}px`;
      }
      animationRef.current.cancel();
      animationRef.current = null;
    }

    el.style.transform = 'none';
    el.style.animation = 'none';

    void el.offsetWidth;
    el.classList.add(styles.dissipating);

    if (onDissipate) {
      onDissipate(id);
    }

    if (autoRemoveTimerRef.current) {
      clearTimeout(autoRemoveTimerRef.current);
    }
  }, [id, onDissipate]);

  useEffect(() => {
    const el = cloudRef.current;
    if (!el) return;

    const screenWidth = window.innerWidth;
    const startX = fromLeft ? -150 : screenWidth + 50;
    const endTranslateX = fromLeft
      ? screenWidth + 300
      : -(screenWidth + 300);
    const totalDurationMs = duration * 1000;

    // Generate keyframes for sinusoidal drift
    const totalSteps = 30;
    const keyframes = [];
    for (let step = 0; step <= totalSteps; step++) {
      const progress = step / totalSteps;
      const x = progress * endTranslateX;
      const y = Math.sin(progress * Math.PI * 2 * frequency) * amplitude;
      keyframes.push({
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
        offset: progress,
      });
    }

    // Set initial position
    el.style.left = `${startX}px`;
    el.style.top = `${startY}px`;

    // Start drift animation
    animationRef.current = el.animate(keyframes, {
      duration: totalDurationMs,
      easing: 'linear',
      fill: 'forwards',
    });

    // Auto-remove after duration (silent, no score)
    autoRemoveTimerRef.current = setTimeout(() => {
      if (!isDissipatedRef.current && onExpire) {
        onExpire(id);
      }
    }, totalDurationMs);

    // --- Drag handling ---
    let isDragging = false;
    let dragStartMouseX = 0;
    let dragStartMouseY = 0;
    let elStartLeft = 0;
    let elStartTop = 0;
    let totalDragDistance = 0;
    let savedCurrentTime = 0;

    const handleMouseDown = (e) => {
      if (isDissipatedRef.current) return;
      e.preventDefault();

      isDragging = true;
      totalDragDistance = 0;

      // Snapshot current visual position & time, then cancel animation
      if (animationRef.current) {
        const computedStyle = window.getComputedStyle(el);
        const matrix = new DOMMatrixReadOnly(computedStyle.transform);
        elStartLeft = el.offsetLeft + matrix.m41;
        elStartTop = el.offsetTop + matrix.m42;

        savedCurrentTime = animationRef.current.currentTime || 0;
        animationRef.current.cancel();
        animationRef.current = null;
      } else {
        elStartLeft = el.offsetLeft;
        elStartTop = el.offsetTop;
        savedCurrentTime = totalDurationMs;
      }

      dragStartMouseX = e.clientX;
      dragStartMouseY = e.clientY;

      el.style.zIndex = '100';
      el.style.left = `${elStartLeft}px`;
      el.style.top = `${elStartTop}px`;
      el.style.transform = `scale(${scale})`;
    };

    const handleMouseMove = (e) => {
      if (!isDragging || isDissipatedRef.current) return;

      const dx = e.clientX - dragStartMouseX;
      const dy = e.clientY - dragStartMouseY;
      totalDragDistance = Math.sqrt(dx * dx + dy * dy);

      el.style.left = `${elStartLeft + dx}px`;
      el.style.top = `${elStartTop + dy}px`;
    };

    const handleMouseUp = () => {
      if (!isDragging || isDissipatedRef.current) return;
      isDragging = false;

      if (totalDragDistance < 3) {
        // Click → dissipate
        dissipate();
      } else {
        // Drag ended → resume drift from current position
        el.style.zIndex = '5';

        const remainingMs = totalDurationMs - savedCurrentTime;

        if (remainingMs > 100) {
          const progressStart = savedCurrentTime / totalDurationMs;
          const remainingX = (1 - progressStart) * endTranslateX;
          const yAtPause = Math.sin(progressStart * Math.PI * 2 * frequency) * amplitude;
          const newKeyframes = [];
          const steps = Math.max(5, Math.round((1 - progressStart) * 30));

          for (let i = 0; i <= steps; i++) {
            const localProgress = i / steps;
            // Horizontal: drift remaining distance from current position
            const x = localProgress * remainingX;
            // Vertical: continue sine wave, relative to pause point
            const globalProgress = progressStart + localProgress * (1 - progressStart);
            const y = Math.sin(globalProgress * Math.PI * 2 * frequency) * amplitude - yAtPause;

            newKeyframes.push({
              transform: `translate(${x}px, ${y}px) scale(${scale})`,
              offset: localProgress,
            });
          }

          animationRef.current = el.animate(newKeyframes, {
            duration: remainingMs,
            easing: 'linear',
            fill: 'forwards',
          });

          // Reset auto-remove timer for remaining time
          if (autoRemoveTimerRef.current) {
            clearTimeout(autoRemoveTimerRef.current);
          }
          autoRemoveTimerRef.current = setTimeout(() => {
            if (!isDissipatedRef.current && onExpire) {
              onExpire(id);
            }
          }, remainingMs);
        }
      }
    };

    el.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      el.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);

      if (animationRef.current) {
        animationRef.current.cancel();
      }
      if (autoRemoveTimerRef.current) {
        clearTimeout(autoRemoveTimerRef.current);
      }
    };
  }, [
    id,
    startY,
    fromLeft,
    scale,
    duration,
    amplitude,
    frequency,
    onExpire,
    dissipate,
  ]);

  return (
    <div
      ref={cloudRef}
      className={styles.cloud}
      style={{
        background: color,
        transform: `scale(${scale})`,
      }}
    />
  );
}
