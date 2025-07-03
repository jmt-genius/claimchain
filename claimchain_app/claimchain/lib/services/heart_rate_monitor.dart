import 'dart:async';
import 'dart:math';
import '../models/heart_rate_data.dart';
import '../models/cardiac_event.dart';
import 'fitbit_service.dart';
import 'database_service.dart';

class HeartRateMonitor {
  final FitbitService _fitbitService = FitbitService();
  final DatabaseService _databaseService = DatabaseService();

  Timer? _timer;
  bool _isMonitoring = false;
  bool _isSimulationMode = true;

  // Simulation parameters
  int _baselineHeartRate = 70;
  int _currentHeartRate = 70;
  int _spikeCounter = 0;

  // Callbacks
  Function(int)? onHeartRateUpdate;
  Function(CardiacEvent)? onCardiacEventDetected;

  // Heart rate history for spike detection
  final List<HeartRateData> _heartRateHistory = [];
  static const int _maxHistorySize = 60; // Keep last 60 data points

  bool get isMonitoring => _isMonitoring;
  bool get isSimulationMode => _isSimulationMode;
  List<HeartRateData> get heartRateHistory =>
      List.unmodifiable(_heartRateHistory);

  void startMonitoring({bool simulationMode = true}) {
    if (_isMonitoring) return;

    _isSimulationMode = simulationMode;
    _isMonitoring = true;

    if (simulationMode) {
      _startSimulationMode();
    } else {
      _startLiveMode();
    }
  }

  void stopMonitoring() {
    _isMonitoring = false;
    _timer?.cancel();
    _timer = null;
  }

  void _startSimulationMode() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _generateSimulatedHeartRate();
    });
  }

  void _startLiveMode() async {
    // Initial authentication
    final authenticated = await _fitbitService.authenticate();
    if (!authenticated) {
      print('Failed to authenticate with Fitbit');
      return;
    }

    _timer = Timer.periodic(const Duration(minutes: 1), (timer) async {
      await _fetchLiveHeartRateData();
    });
  }

  void _generateSimulatedHeartRate() {
    final random = Random();

    // Generate occasional spikes
    if (_spikeCounter == 0 && random.nextDouble() < 0.1) {
      // 10% chance every second
      _currentHeartRate =
          _baselineHeartRate + random.nextInt(80) + 40; // Spike to 110-190
      _spikeCounter = random.nextInt(5) + 3; // Spike duration 3-7 seconds
    } else if (_spikeCounter > 0) {
      _spikeCounter--;
      if (_spikeCounter == 0) {
        _currentHeartRate =
            _baselineHeartRate +
            random.nextInt(10) -
            5; // Return to baseline ±5
      }
    } else {
      // Normal variation
      _currentHeartRate =
          _baselineHeartRate + random.nextInt(21) - 10; // ±10 from baseline
    }

    _addHeartRateData(_currentHeartRate);
    _checkForCardiacSpike();
  }

  Future<void> _fetchLiveHeartRateData() async {
    try {
      final heartRateData = await _fitbitService.getHeartRateData();

      for (final data in heartRateData) {
        _addHeartRateData(data.heartRate);
      }

      _checkForCardiacSpike();
    } catch (e) {
      print('Error fetching live heart rate data: $e');
    }
  }

  void _addHeartRateData(int heartRate) {
    final data = HeartRateData(timestamp: DateTime.now(), heartRate: heartRate);

    _heartRateHistory.add(data);

    // Keep only the last N data points
    if (_heartRateHistory.length > _maxHistorySize) {
      _heartRateHistory.removeAt(0);
    }

    onHeartRateUpdate?.call(heartRate);
  }

  void _checkForCardiacSpike() {
    if (_heartRateHistory.length < 2) return;

    final currentHR = _heartRateHistory.last.heartRate;
    final previousHR =
        _heartRateHistory[_heartRateHistory.length - 2].heartRate;

    // Check for spike detection: HR > 130 and spike > 40 bpm from baseline
    if (currentHR > 130 && (currentHR - previousHR) > 40) {
      _handleCardiacSpike(currentHR);
    }
  }

  void _handleCardiacSpike(int heartRate) async {
    final event = CardiacEvent(
      customerId: 'user_123', // Replace with actual user ID
      timestamp: DateTime.now(),
      heartRate: heartRate,
      mode: _isSimulationMode ? 'simulation' : 'live',
      summary: _generateEventSummary(heartRate),
    );

    // Save to database
    await _databaseService.saveCardiacEvent(event);

    // Notify listeners
    onCardiacEventDetected?.call(event);
  }

  String _generateEventSummary(int heartRate) {
    final mode = _isSimulationMode ? 'simulation' : 'live monitoring';
    final riskLevel = heartRate > 150 ? 'high-risk' : 'moderate-risk';
    return '$riskLevel cardiac spike detected during $mode';
  }

  void dispose() {
    stopMonitoring();
  }
}
