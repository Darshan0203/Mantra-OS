import React, {useRef} from 'react';
import {Animated, Pressable, Text} from 'react-native';
import Ionicons from '@react-native-vector-icons/ionicons';
import {styles} from './VoiceButton.styles';

const VoiceButton = () => {
  const scale = useRef(new Animated.Value(1)).current;

  const pressIn = () => {
    Animated.spring(scale, {
      toValue: 0.92,
      useNativeDriver: true,
    }).start();
  };

  const pressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      friction: 3,
      useNativeDriver: true,
    }).start();
  };

  return (
    <Animated.View
      style={[
        styles.container,
        {
          transform: [{scale}],
        },
      ]}>
      <Pressable
        onPressIn={pressIn}
        onPressOut={pressOut}>
        <Animated.View style={styles.button}>
          <Ionicons name="mic" color="#000" size={30} />
        </Animated.View>
      </Pressable>

      <Text style={styles.text}>
        Hold to Talk
      </Text>
    </Animated.View>
  );
};

export default VoiceButton;