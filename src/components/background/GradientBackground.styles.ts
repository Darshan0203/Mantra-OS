import { StyleSheet } from 'react-native';
import { Theme } from '../../theme';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Theme.colors.background,
  },

  gradient: {
    ...StyleSheet.absoluteFill,
  },

  content: {
    flex: 1,
    padding: Theme.spacing.lg,
  },
});