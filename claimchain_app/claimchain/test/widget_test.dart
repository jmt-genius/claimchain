// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:claimchain/main.dart';
import 'package:claimchain/providers/heart_rate_provider.dart';

void main() {
  testWidgets('Claimchain app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ClaimchainApp());

    // Verify that the app title is displayed
    expect(find.text('Claimchain'), findsOneWidget);

    // Verify that the mode toggle is present
    expect(find.text('Monitoring Mode'), findsOneWidget);
    expect(find.text('Simulation'), findsOneWidget);

    // Verify that heart rate display is present
    expect(find.text('Current Heart Rate'), findsOneWidget);
    expect(find.text('BPM'), findsOneWidget);

    // Verify that control buttons are present
    expect(find.text('Start Monitoring'), findsOneWidget);
    expect(find.text('Sync to Server'), findsOneWidget);
  });
}
