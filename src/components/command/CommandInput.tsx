import React, {useState} from 'react';
import {
  NativeModules,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import {sendCommand} from '../../services/api';

const {MantraAppLauncher} = NativeModules;

type CommandAction = {
  action: string;
  app?: string;
  contact?: string;
  message?: string;
  query?: string;
  target?: string;
};

const APP_PACKAGES: Record<string, string> = {
  youtube: 'com.google.android.youtube',
  chrome: 'com.android.chrome',
  whatsapp: 'com.whatsapp',
  instagram: 'com.instagram.android',
  settings: 'com.android.settings',
};

const CommandInput = () => {
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  // ================================================================
  // WHATSAPP EXECUTION
  // ================================================================

  const processWhatsAppActions = async (
    actions: CommandAction[],
  ) => {
    for (const action of actions) {
      if (action.app?.toLowerCase() !== 'whatsapp') {
        continue;
      }

      if (action.action === 'launch_app') {
        console.log('MANTRA: Opening WhatsApp...');

        MantraAppLauncher.launchApp(
          APP_PACKAGES.whatsapp,
        );

        await new Promise<void>(resolve =>
          setTimeout(resolve, 2500),
        );
      }

      if (action.action === 'open_contact') {
        console.log(
          'MANTRA: Opening WhatsApp contact:',
          action.contact,
        );

        if (action.contact) {
          MantraAppLauncher.openWhatsAppContact(
            action.contact,
          );
        }

        await new Promise<void>(resolve =>
          setTimeout(resolve, 3000),
        );
      }

      if (action.action === 'send_message') {
        console.log(
          'MANTRA: Sending WhatsApp message:',
          action.message,
        );

        if (action.message) {
          MantraAppLauncher.sendWhatsAppMessage(
            action.message,
          );
        }

        await new Promise<void>(resolve =>
          setTimeout(resolve, 5000),
        );

        console.log(
          'MANTRA: WhatsApp operation finished.',
        );

        MantraAppLauncher.returnToMantra();

        await new Promise<void>(resolve =>
          setTimeout(resolve, 1500),
        );
      }
    }
  };

  // ================================================================
  // HANDLE COMMAND
  // ================================================================

  const handleCommand = async () => {
    const trimmedCommand = command.trim();

    if (!trimmedCommand || loading) {
      return;
    }

    setLoading(true);
    setResponse('');

    try {
      console.log('================================');
      console.log(
        'MANTRA COMMAND:',
        trimmedCommand,
      );
      console.log('================================');

      const result = await sendCommand(
        trimmedCommand,
      );

      console.log(
        'MANTRA BACKEND RESULT:',
        JSON.stringify(
          result,
          null,
          2,
        ),
      );

      const executionActions = (
        result.result?.actions ?? []
      )
        .map(item => {
          const actionItem = item as {
            action?: CommandAction;
          };

          return actionItem.action;
        })
        .filter(
          (
            action,
          ): action is CommandAction =>
            !!action,
        );

      console.log(
        'MANTRA EXECUTION ACTIONS:',
        executionActions,
      );

      // Only WhatsApp actions are executed here.
      // YouTube is already executed by the backend
      // through Playwright.
      await processWhatsAppActions(
        executionActions,
      );

      setResponse(
        JSON.stringify(
          result,
          null,
          2,
        ),
      );

      setCommand('');

    } catch (error: any) {

      console.error(
        'MANTRA BACKEND ERROR:',
        error,
      );

      setResponse(
        JSON.stringify(
          {
            status: 'error',
            error:
              error?.response?.data ||
              error?.message ||
              String(error),
          },
          null,
          2,
        ),
      );

    } finally {
      setLoading(false);
    }
  };

  // ================================================================
  // UI
  // ================================================================

  return (
    <View style={styles.container}>

      <View style={styles.inputContainer}>

        <TextInput
          value={command}
          onChangeText={setCommand}
          placeholder="Ask MANTRA anything..."
          placeholderTextColor="#777"
          style={styles.input}
          multiline
          editable={!loading}
          onSubmitEditing={handleCommand}
        />

        <Pressable
          onPress={handleCommand}
          disabled={loading}
          style={[
            styles.sendButton,
            loading && styles.disabledButton,
          ]}
        >
          <Text style={styles.sendText}>
            {loading ? '...' : '➤'}
          </Text>
        </Pressable>

      </View>

      {response.length > 0 && (
        <View style={styles.responseContainer}>

          <Text style={styles.responseTitle}>
            MANTRA RESPONSE
          </Text>

          <Text style={styles.responseText}>
            {response}
          </Text>

        </View>
      )}

    </View>
  );
};

// ================================================================
// STYLES
// ================================================================

const styles = StyleSheet.create({
  container: {
    width: '100%',
    paddingHorizontal: 20,
    marginTop: 20,
  },

  inputContainer: {
    minHeight: 60,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#333',
    backgroundColor: '#15151f',
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: 16,
    paddingRight: 8,
  },

  input: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    paddingVertical: 14,
    maxHeight: 120,
  },

  sendButton: {
    width: 45,
    height: 45,
    borderRadius: 23,
    backgroundColor: '#6C63FF',
    justifyContent: 'center',
    alignItems: 'center',
  },

  disabledButton: {
    opacity: 0.5,
  },

  sendText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },

  responseContainer: {
    marginTop: 15,
    padding: 15,
    borderRadius: 15,
    backgroundColor: '#101018',
    borderWidth: 1,
    borderColor: '#292938',
  },

  responseTitle: {
    color: '#6C63FF',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 8,
  },

  responseText: {
    color: '#ccc',
    fontSize: 12,
    lineHeight: 18,
  },
});

export default CommandInput;