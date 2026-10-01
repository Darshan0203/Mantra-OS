import React, {useEffect, useRef} from 'react';
import {Animated} from 'react-native';
import {styles} from './AIOrb.styles';

const AIOrb = () => {
  const scale = useRef(new Animated.Value(1)).current;
  const translateY = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.parallel([
        Animated.sequence([
          Animated.timing(scale, {
            toValue: 1.08,
            duration: 1800,
            useNativeDriver: true,
          }),
          Animated.timing(scale, {
            toValue: 1,
            duration: 1800,
            useNativeDriver: true,
          }),
        ]),

        Animated.sequence([
          Animated.timing(translateY, {
            toValue: -8,
            duration: 1800,
            useNativeDriver: true,
          }),
          Animated.timing(translateY, {
            toValue: 8,
            duration: 1800,
            useNativeDriver: true,
          }),
        ]),
      ]),
    ).start();
  }, []);

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{scale}, {translateY}],
        },
      ]}>
      <Animated.View style={styles.glow}>
        <Animated.View style={styles.orb} />
      </Animated.View>
    </Animated.View>
  );
};

export default AIOrb;