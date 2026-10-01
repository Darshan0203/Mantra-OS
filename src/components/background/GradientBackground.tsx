import React from 'react';
import { View } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import { styles } from './GradientBackground.styles';

type Props = {
  children: React.ReactNode;
};

const GradientBackground = ({ children }: Props) => {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[
          '#05070F',
          '#10131F',
          '#24194a',
          '#05070F',
        ]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradient}
      />

      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
};

export default GradientBackground;