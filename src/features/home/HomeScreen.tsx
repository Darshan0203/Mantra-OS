import React from 'react';
import {
  SafeAreaView,
  ScrollView,
  Text,
  View,
} from 'react-native';

import GradientBackground from '../../components/background';
import AIOrb from '../../components/orb';
import VoiceButton from '../../components/buttons';
import CommandInput from '../../components/command';

import {styles} from './Home.styles';

const HomeScreen = () => {
  return (
    <GradientBackground>
      <SafeAreaView style={styles.container}>
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.contentContainer}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="on-drag">

          <View style={styles.header}>
            <Text style={styles.title}>
              MANTRA
            </Text>

            <Text style={styles.subtitle}>
              Your Personal AI Operating System
            </Text>
          </View>

          <AIOrb />

          <Text style={styles.prompt}>
            How can I help you today?
          </Text>

          <VoiceButton />

          <CommandInput />

        </ScrollView>
      </SafeAreaView>
    </GradientBackground>
  );
};

export default HomeScreen;