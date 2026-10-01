import {StyleSheet} from 'react-native';

export const styles = StyleSheet.create({
  container: {
    width: '90%',
    alignSelf: 'center',
    marginTop: 24,
  },

  inputContainer: {
    minHeight: 58,
    flexDirection: 'row',
    alignItems: 'center',

    backgroundColor: 'rgba(255,255,255,0.08)',

    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.15)',

    borderRadius: 20,

    paddingLeft: 18,
    paddingRight: 8,
  },

  input: {
    flex: 1,
    color: '#FFFFFF',
    fontSize: 16,
  },

  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,

    justifyContent: 'center',
    alignItems: 'center',

    backgroundColor: '#6C63FF',
  },

  response: {
    marginTop: 16,
    padding: 16,

    borderRadius: 18,

    backgroundColor: 'rgba(255,255,255,0.06)',

    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },

  responseText: {
    color: '#FFFFFF',
    fontSize: 15,
    lineHeight: 22,
  },

  loading: {
    color: '#AAAAAA',
    fontSize: 14,
  },

  error: {
    color: '#FF6B6B',
    fontSize: 14,
  },
});