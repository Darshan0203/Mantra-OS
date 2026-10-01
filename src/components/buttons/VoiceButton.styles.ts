import {StyleSheet} from 'react-native';
import {Theme} from '../../theme';

export const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginTop: Theme.spacing.xl,
  },

  button: {
    width: 78,
    height: 78,
    borderRadius: 39,
    backgroundColor: Theme.colors.primary,

    justifyContent: 'center',
    alignItems: 'center',

    shadowColor: Theme.colors.primary,
    shadowOpacity: 0.5,
    shadowRadius: 20,
    shadowOffset: {
      width: 0,
      height: 8,
    },

    elevation: 10,
  },

  text: {
    marginTop: Theme.spacing.md,
    color: Theme.colors.white,
    fontSize: Theme.typography.body,
    fontWeight: '600',
  },
});