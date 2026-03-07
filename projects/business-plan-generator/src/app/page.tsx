'use client';

import { useAppContext } from '@/context/AppContext';
import { SetupScreen } from '@/components/SetupScreen';
import { WizardScreen } from '@/components/WizardScreen';
import { PipelineScreen } from '@/components/PipelineScreen';
import { OutputScreen } from '@/components/OutputScreen';

export default function Home() {
  const { currentStep } = useAppContext();

  switch (currentStep) {
    case 'setup':
      return <SetupScreen />;
    case 'wizard':
      return <WizardScreen />;
    case 'pipeline':
      return <PipelineScreen />;
    case 'output':
      return <OutputScreen />;
    default:
      return <SetupScreen />;
  }
}