import { useCallback } from 'react';
import BackgroundOrbs from '../BackgroundOrbs/BackgroundOrbs';
import Cloud from '../Cloud/Cloud';
import ScoreBoard from '../ScoreBoard/ScoreBoard';
import VolumeControl from '../VolumeControl/VolumeControl';
import useAudio from '../../hooks/useAudio';
import useScore from '../../hooks/useScore';
import useCloudSpawner from '../../hooks/useCloudSpawner';

export default function CloudGameLayer({ spawnRate = 'normal', initialClouds = 3 }) {
  const { playPop, playBtn, setVolume } = useAudio();
  const { score, addScore, resetScore } = useScore();
  const { clouds, spawnCloud, removeCloud } = useCloudSpawner(spawnRate);

  const handleDissipate = useCallback(
    (id) => {
      addScore();
      playPop();
      setTimeout(() => {
        removeCloud(id);
      }, 400);
    },
    [removeCloud, addScore, playPop]
  );

  // Silent remove when cloud drifts off screen (no score, no sound)
  const handleExpire = useCallback(
    (id) => {
      removeCloud(id);
    },
    [removeCloud]
  );

  return (
    <>
      <BackgroundOrbs />
      {clouds.map((cloud) => (
        <Cloud
          key={cloud.id}
          id={cloud.id}
          color={cloud.color}
          startY={cloud.startY}
          fromLeft={cloud.fromLeft}
          scale={cloud.scale}
          duration={cloud.duration}
          amplitude={cloud.amplitude}
          frequency={cloud.frequency}
          onDissipate={handleDissipate}
          onExpire={handleExpire}
        />
      ))}
      <ScoreBoard score={score} />
      <VolumeControl onVolumeChange={setVolume} />
    </>
  );
}
