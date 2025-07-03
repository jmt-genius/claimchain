import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/heart_rate_provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const ClaimchainApp());
}

class ClaimchainApp extends StatelessWidget {
  const ClaimchainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => HeartRateProvider(),
      child: MaterialApp(
        title: 'Claimchain',
        theme: ThemeData(
          primarySwatch: Colors.red,
          primaryColor: Colors.red.shade700,
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.red.shade700,
            brightness: Brightness.light,
          ),
          useMaterial3: true,
          appBarTheme: AppBarTheme(
            backgroundColor: Colors.red.shade700,
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          cardTheme: CardThemeData(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
        home: const HomeScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
