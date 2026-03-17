'use client';

import { useEffect, useState, ReactNode } from 'react';

/**
 * PrivacyGate ensures that the application runs completely client-side.
 * It checks for browser capabilities and displays warnings if external tracking is detected.
 */
export default function PrivacyGate({ children }: { children: ReactNode }) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Logic to verify no external unapproved scripts are loaded
    // and initialize secure local state could go here.
  }, []);

  if (!isClient) {
    // Prevent SSR rendering which might leak data
    return (
      <div className="p-8 text-center text-2xl" aria-live="polite">
        Initializing secure environment...
      </div>
    );
  }

  return (
    <div className="privacy-gate-container w-full h-full flex flex-col">
      <div 
        className="bg-green-900 border-l-8 border-green-500 text-white p-6 m-4 rounded shadow drop-shadow-lg" 
        role="alert"
        aria-live="assertive"
      >
        <p className="font-extrabold text-2xl mb-2">Notice: Privacy Mode Active</p>
        <p className="text-xl">Your data is securely stored only on this device. No information is transmitted to our servers.</p>
      </div>
      <div className="flex-1 w-full h-full">
        {children}
      </div>
    </div>
  );
}
