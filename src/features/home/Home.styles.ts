import {StyleSheet} from 'react-native';
import {Theme} from '../../theme';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
  },

  scrollView: {
    flex: 1,
  },

  contentContainer: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingBottom: 40,
    paddingTop: 20,
    justifyContent: 'center',
  },

  header: {
    alignItems: 'center',
    marginTop: 30,
  },

  title: {
    fontSize: 42,
    fontWeight: '700',
    color: Theme.colors.white,
    letterSpacing: 2,
  },

  subtitle: {
    marginTop: 10,
    fontSize: 18,
    color: Theme.colors.textSecondary,
    textAlign: 'center',
  },

  prompt: {
    textAlign: 'center',
    color: Theme.colors.white,
    fontSize: 18,
    marginBottom: 10,
  },
});