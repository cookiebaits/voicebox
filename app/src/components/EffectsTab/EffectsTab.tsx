import { EffectsDetail } from './EffectsDetail';
import { EffectsList } from './EffectsList';

export function EffectsTab() {
  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden -mx-4 md:-mx-8">
      <div className="flex-1 min-h-0 flex flex-col md:flex-row gap-4 md:gap-6 overflow-hidden">
        {/* Left - Presets list */}
        <div className="w-full md:max-w-[360px] shrink-0 flex flex-col min-h-0">
          <EffectsList />
        </div>

        {/* Right - Detail / editor */}
        <div className="flex-1 min-h-0 flex flex-col px-4 md:px-0 md:pr-8">
          <EffectsDetail />
        </div>
      </div>
    </div>
  );
}
