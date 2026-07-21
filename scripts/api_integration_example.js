/**
 * Voicebox API Integration Script
 *
 * This script demonstrates how to integrate Voicebox into an external webpage
 * or system (e.g., hosted on Dokploy behind a Cloudflare proxy).
 * Voicebox can consume significant resources, so offloading TTS generation
 * to a dedicated instance allows your main web applications to remain light and responsive.
 *
 * Usage Requirements:
 * 1. Node.js environment or standard web browser.
 * 2. Update the `VOICEBOX_URL` to point to your deployed Voicebox instance.
 * 3. Have at least one Voice Profile ID configured in Voicebox to generate speech.
 */

const VOICEBOX_URL = 'https://your-dokploy-voicebox.example.com';
const PROFILE_ID = 'your_voice_profile_id_here';
// Example text to convert to speech
const TEXT_TO_SPEAK = 'Hello, this is a demonstration of Voicebox API integration for resource-heavy operations.';

/**
 * Initiates a Text-to-Speech generation request.
 */
async function generateSpeech(text, profileId) {
  try {
    console.log(`Sending TTS generation request to ${VOICEBOX_URL}...`);

    // Call the /generate endpoint
    const response = await fetch(`${VOICEBOX_URL}/api/v1/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // If Voicebox requires authentication (e.g. bearer token), include it here:
        // 'Authorization': 'Bearer YOUR_API_TOKEN'
      },
      body: JSON.stringify({
        profile_id: profileId,
        text: text,
        language: 'en', // Change as needed
        engine: 'chatterbox_turbo' // Defaults to chatterbox_turbo
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to generate speech: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Generation request successful. Generation ID:', data.id);

    // Depending on the backend implementation, /generate may return immediately
    // with a generation ID that you must poll, or it may return the completed audio path.
    // If polling is required, you can poll `/api/v1/history` or `/api/v1/generations/{id}/status`.

    return data;
  } catch (error) {
    console.error('Error in generateSpeech:', error);
    throw error;
  }
}

/**
 * Polls for completion and returns the final audio URL.
 */
async function waitForAudioCompletion(generationId) {
  let attempt = 0;
  const maxAttempts = 30; // Wait up to 30 seconds
  const delay = 1000; // 1 second

  while (attempt < maxAttempts) {
    console.log(`Polling status for generation ${generationId}... (Attempt ${attempt + 1}/${maxAttempts})`);

    // Assuming a status endpoint or fetching history by ID
    // Update path as appropriate based on your exact Voicebox routing for status polling.
    // E.g., `GET /api/v1/history?search=${generationId}`
    const response = await fetch(`${VOICEBOX_URL}/api/v1/history`, {
      headers: {
        'Accept': 'application/json'
      }
    });

    if (response.ok) {
      const result = await response.json();
      // Find the specific generation in history
      const gen = result.items.find(item => item.id === generationId);

      if (gen) {
        if (gen.status === 'completed' && gen.audio_path) {
          const audioUrl = `${VOICEBOX_URL}${gen.audio_path}`;
          console.log(`Generation completed successfully! Audio URL: ${audioUrl}`);
          return audioUrl;
        } else if (gen.status === 'failed') {
          throw new Error('Generation failed on the server.');
        }
      }
    }

    await new Promise(resolve => setTimeout(resolve, delay));
    attempt++;
  }

  throw new Error('Timed out waiting for audio generation.');
}

// Example execution
async function main() {
  try {
    const generationResult = await generateSpeech(TEXT_TO_SPEAK, PROFILE_ID);

    // If the generation is async, poll for the audio path
    if (generationResult.status === 'generating' || generationResult.status === 'loading_model') {
      const audioUrl = await waitForAudioCompletion(generationResult.id);
      console.log('You can now embed or play the audio from:', audioUrl);

      // In a browser context, you could play it directly:
      // const audio = new Audio(audioUrl);
      // audio.play();
    } else if (generationResult.audio_path) {
      // If generated synchronously
      console.log('Audio generated instantly:', `${VOICEBOX_URL}${generationResult.audio_path}`);
    }
  } catch (err) {
    console.error('Integration demonstration failed:', err);
  }
}

// Run the demonstration if executed directly (e.g. `node api_integration_example.js`)
if (typeof require !== 'undefined' && require.main === module) {
  main();
}
