import {apiClient} from './client';

export interface CommandRequest {
  command: string;
}

export interface CommandResponse {
  status: string;
  result?: {
    plan?: {
      plan?: unknown[];
      [key: string]: unknown;
    };
    actions?: unknown[];
    context?: Record<string, unknown>;
  };
  error?: string;
}

export const sendCommand = async (
  command: string,
): Promise<CommandResponse> => {
  const response = await apiClient.post<CommandResponse>('/command', {
    command,
  });

  return response.data;
};