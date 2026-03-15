/**
 * Utility for WebAuthn (FaceID/Fingerprint) integration
 */
export async function authenticateWithBiometrics(): Promise<boolean> {
  if (typeof window === 'undefined' || !window.PublicKeyCredential) {
    console.error("WebAuthn is not supported in this environment.");
    return false;
  }

  try {
    // For a local-only approach without a traditional backend server,
    // we use a dummy assertion challenge to prompt the user's local biometric check.
    const challenge = new Uint8Array(32);
    crypto.getRandomValues(challenge);

    const assertion = await navigator.credentials.get({
      publicKey: {
        challenge: challenge,
        timeout: 60000,
        // userVerification: 'required' ensures biometrics/PIN are explicitly used
        userVerification: 'required'
      }
    });

    if (assertion) {
      return true;
    }
    return false;
  } catch (error) {
    console.error("Biometric authentication failed or was cancelled by user.", error);
    return false;
  }
}

/**
 * Note: A full local-only WebAuthn flow would still require storing 
 * credential IDs in localStorage (alongside securely encrypted data).
 * 
 * We omit credential creation (navigator.credentials.create) here 
 * for brevity, but it would look similar.
 */
