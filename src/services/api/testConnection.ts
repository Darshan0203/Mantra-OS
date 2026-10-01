import {sendCommand} from './mantraApi';

export const testMantraBackend = async () => {
  try {
    const response = await sendCommand('Hello MANTRA');

    console.log('MANTRA BACKEND RESPONSE:', response);

    return response;
  } catch (error) {
    console.error('MANTRA BACKEND ERROR:', error);
    throw error;
  }
};