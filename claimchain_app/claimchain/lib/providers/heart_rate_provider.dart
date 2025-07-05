import 'package:flutter/foundation.dart';
import '../models/cardiac_event.dart';
import '../models/heart_rate_data.dart';
import '../services/heart_rate_monitor.dart';
import '../services/api_service.dart';

class HeartRateProvider with ChangeNotifier {
  final HeartRateMonitor _monitor = HeartRateMonitor();
  final ApiService _apiService = ApiService();

  int _currentHeartRate = 70;
  bool _isSimulationMode = true;
  bool _isMonitoring = false;
  CardiacEvent? _latestEvent;
  String _syncStatus = '';

  int get currentHeartRate => _currentHeartRate;
  bool get isSimulationMode => _isSimulationMode;
  bool get isMonitoring => _isMonitoring;
  CardiacEvent? get latestEvent => _latestEvent;
  String get syncStatus => _syncStatus;
  List<HeartRateData> get heartRateHistory => _monitor.heartRateHistory;

  HeartRateProvider() {
    _setupMonitorCallbacks();
  }

  void _setupMonitorCallbacks() {
    _monitor.onHeartRateUpdate = (heartRate) {
      _currentHeartRate = heartRate;
      notifyListeners();
    };

    _monitor.onCardiacEventDetected = (event) {
      _latestEvent = event;
      notifyListeners();
    };
  }

  void toggleMode() {
    _isSimulationMode = !_isSimulationMode;
    if (_isMonitoring) {
      stopMonitoring();
      startMonitoring();
    }
    notifyListeners();
  }

  void startMonitoring() {
    _isMonitoring = true;
    _monitor.startMonitoring(simulationMode: _isSimulationMode);
    notifyListeners();
  }

  void stopMonitoring() {
    _isMonitoring = false;
    _monitor.stopMonitoring();
    notifyListeners();
  }

  Future<void> syncToServer() async {
    if (_latestEvent == null) {
      _syncStatus = 'No cardiac event to sync';
      notifyListeners();
      return;
    }

    _syncStatus = 'Syncing...';
    notifyListeners();

    final success = await _apiService.syncCardiacEvent(_latestEvent!);

    if (success) {
      _syncStatus = '✅ Latest cardiac event synced';
    } else {
      _syncStatus = '❌ Sync failed';
    }

    notifyListeners();
  }

  void clearSyncStatus() {
    _syncStatus = '';
    notifyListeners();
  }

  @override
  void dispose() {
    _monitor.dispose();
    super.dispose();
  }
}
