import 'package:flutter/foundation.dart';
import '../models/cardiac_event.dart';
import '../models/heart_rate_data.dart';
import '../services/heart_rate_monitor.dart';
import '../services/api_service.dart';
import 'dart:async';

class HeartRateProvider with ChangeNotifier {
  final HeartRateMonitor _monitor = HeartRateMonitor();
  final ApiService _apiService = ApiService();

  int _currentHeartRate = 70;
  bool _isSimulationMode = true;
  bool _isMonitoring = false;
  CardiacEvent? _latestEvent;
  String _syncStatus = '';
  bool _isRangeSimulation = false;
  int _rangeMin = 60;
  int _rangeMax = 100;
  int _rangeCurrent = 60;
  bool _rangeIncreasing = true;
  Timer? _rangeTimer;
  VoidCallback? _onRangeStop;
  final List<HeartRateData> _rangeSimulationHistory = [];
  String _customerId = '';

  int get currentHeartRate => _currentHeartRate;
  bool get isSimulationMode => _isSimulationMode;
  bool get isMonitoring => _isMonitoring;
  CardiacEvent? get latestEvent => _latestEvent;
  String get syncStatus => _syncStatus;
  List<HeartRateData> get heartRateHistory =>
      _isRangeSimulation ? _rangeSimulationHistory : _monitor.heartRateHistory;
  bool get isRangeSimulation => _isRangeSimulation;
  int get rangeMin => _rangeMin;
  int get rangeMax => _rangeMax;
  String get customerId => _customerId;

  HeartRateProvider() {
    _setupMonitorCallbacks();
  }

  void _setupMonitorCallbacks() {
    _monitor.onHeartRateUpdate = (heartRate) {
      if (!_isRangeSimulation) {
        _currentHeartRate = heartRate;
        notifyListeners();
      }
    };

    _monitor.onCardiacEventDetected = (event) {
      if (_isRangeSimulation) return;
      _latestEvent = event;
      notifyListeners();
    };
  }

  void toggleMode() {
    if (_isRangeSimulation) return;
    _isSimulationMode = !_isSimulationMode;
    if (_isMonitoring) {
      stopMonitoring();
      startMonitoring();
    }
    notifyListeners();
  }

  void startMonitoring() {
    if (_isRangeSimulation) return;
    _isMonitoring = true;
    _monitor.startMonitoring(simulationMode: _isSimulationMode);
    notifyListeners();
  }

  void stopMonitoring() {
    if (_isRangeSimulation) return;
    _isMonitoring = false;
    _monitor.stopMonitoring();
    notifyListeners();
  }

  void setCustomerId(String id) {
    _customerId = id;
    notifyListeners();
  }

  Future<void> syncToServer() async {
    if (_customerId.isEmpty) {
      _syncStatus = 'Please enter a customer ID';
      notifyListeners();
      return;
    }

    if (_latestEvent == null) {
      _syncStatus = 'No cardiac event detected yet';
      notifyListeners();
      return;
    }

    _syncStatus = 'Syncing...';
    notifyListeners();

    // Create a new event with the current customer ID but using the latest event's data
    final eventToSync = CardiacEvent(
      customerId: _customerId,
      timestamp: _latestEvent!.timestamp,
      heartRate: _latestEvent!.heartRate,
      mode: _latestEvent!.mode,
      summary: _latestEvent!.summary,
    );

    final success = await _apiService.syncCardiacEvent(eventToSync);

    if (success) {
      _syncStatus = '✅ Cardiac event synced';
    } else {
      _syncStatus = '❌ Sync failed';
    }

    notifyListeners();
  }

  String _generateEventSummary() {
    final mode = _isRangeSimulation
        ? 'range simulation'
        : _isSimulationMode
        ? 'simulation'
        : 'live monitoring';
    final riskLevel = _currentHeartRate > 130 ? 'high' : 'normal';
    return '$riskLevel cardiac event during $mode';
  }

  void clearSyncStatus() {
    _syncStatus = '';
    notifyListeners();
  }

  void startRangeSimulation(int min, int max, {VoidCallback? onStop}) {
    // Stop regular monitoring if it's running
    if (_isMonitoring) {
      _monitor.stopMonitoring();
    }

    // Clear existing simulation data
    _rangeSimulationHistory.clear();

    // Stop existing range simulation
    stopRangeSimulation();

    _isRangeSimulation = true;
    _rangeMin = min;
    _rangeMax = max;
    _rangeCurrent = min;
    _rangeIncreasing = true;
    _onRangeStop = onStop;

    _rangeTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!_isRangeSimulation) return;

      if (_rangeIncreasing) {
        _rangeCurrent++;
        if (_rangeCurrent >= _rangeMax) _rangeIncreasing = false;
      } else {
        _rangeCurrent--;
        if (_rangeCurrent <= _rangeMin) _rangeIncreasing = true;
      }

      _currentHeartRate = _rangeCurrent;

      final newData = HeartRateData(
        timestamp: DateTime.now(),
        heartRate: _rangeCurrent,
      );

      _rangeSimulationHistory.add(newData);
      if (_rangeSimulationHistory.length > 60) {
        _rangeSimulationHistory.removeAt(0);
      }

      notifyListeners();
    });

    notifyListeners();
  }

  void stopRangeSimulation() {
    _isRangeSimulation = false;
    _rangeTimer?.cancel();
    _rangeTimer = null;
    _rangeSimulationHistory.clear();
    _onRangeStop?.call();

    // Restart regular monitoring if it was running
    if (_isMonitoring) {
      _monitor.startMonitoring(simulationMode: _isSimulationMode);
    }

    notifyListeners();
  }

  @override
  void dispose() {
    _rangeTimer?.cancel();
    _monitor.dispose();
    super.dispose();
  }
}
