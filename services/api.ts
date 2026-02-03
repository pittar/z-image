// This file handles communication with the Python backend

const API_URL = 'http://turbo:8000';

export interface GenerationRequest {
  prompt: string;
  height: number;
  width: number;
  steps: number;
  guidanceScale: number;
  seed: number;
  useFlashAttn3: boolean;
}

export const generateImage = async (params: GenerationRequest): Promise<string> => {
  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: params.prompt,
        height: params.height,
        width: params.width,
        num_inference_steps: params.steps,
        guidance_scale: params.guidanceScale,
        seed: params.seed,
        use_flash_attn_3: params.useFlashAttn3
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Generation failed');
    }

    const data = await response.json();
    // Assuming backend returns { image_url: "..." } or { base64: "..." }
    // For this implementation, let's assume it returns a base64 string
    return `data:image/png;base64,${data.image_base64}`;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};
