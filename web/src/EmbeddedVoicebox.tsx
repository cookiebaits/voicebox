import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../../app/src/App';
import '../../app/src/index.css';
import { PlatformProvider } from '../../app/src/platform/PlatformContext';
import { webPlatform } from './platform';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const EmbeddedVoicebox: React.FC = () => {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <PlatformProvider platform={webPlatform}>
          <App />
        </PlatformProvider>
      </QueryClientProvider>
    </React.StrictMode>
  );
};

export default EmbeddedVoicebox;
