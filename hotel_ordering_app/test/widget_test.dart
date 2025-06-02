import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_ordering_app/main.dart';

void main() {
  testWidgets('App builds without crashing', (WidgetTester tester) async {
    // Build the app
    await tester.pumpWidget(const MyApp());

    // Check that a Scaffold exists
    expect(find.byType(Scaffold), findsOneWidget);

    // Check that a loading spinner appears
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
